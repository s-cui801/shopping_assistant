import os
from typing import Annotated
from datetime import datetime
import uuid

from typing_extensions import TypedDict

from langgraph.graph.message import AnyMessage, add_messages

# from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from utilities import handle_tool_error, create_tool_node_with_fallback, _print_event

from langchain_openai import ChatOpenAI

from tools.products_tool import search_product_tool
from tools.cart_tool import fetch_cart_tool, add_to_cart_tool
from tools.order_tool import create_order_tool
from tools.policy_tool import check_discount_tool


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            configuration = config.get("configurable", {})
            customer_id = configuration.get("customer_id", None)
            state = {**state, "user_info": customer_id}
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}


llm = ChatOpenAI(model="gpt-4-turbo-preview")

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful shopping assistant. "
            " Use the provided tools to search for products, shopping cart items, order statuses, policies and other information to assist the user's queries. "
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            " When searching, you are strictly limited to the database provided. "
            " When adding items to the cart, ensure that the item is in stock and that the quantity is available. "
            " When adding items to the cart, ask user to confirm the quantity and the product before adding it to the cart. If the item is already in the cart, ask the user to confirm the operation; if the user confirms, update the quantity of the item in the cart. "
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)

part_1_tools = [
    TavilySearchResults(max_results=2),
    search_product_tool,
    fetch_cart_tool,
    add_to_cart_tool,
    create_order_tool,
    check_discount_tool,
    
    # fetch_user_flight_information,
    # search_flights,
    # lookup_policy,
    # update_ticket_to_new_flight,
    # cancel_ticket,
    # search_car_rentals,
    # book_car_rental,
    # update_car_rental,
    # cancel_car_rental,
    # search_hotels,
    # book_hotel,
    # update_hotel,
    # cancel_hotel,
    # search_trip_recommendations,
    # book_excursion,
    # update_excursion,
    # cancel_excursion,
]
part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(part_1_tools)

# Create the graph
builder = StateGraph(State)


# Define nodes: these do the work
builder.add_node("assistant", Assistant(part_1_assistant_runnable))
builder.add_node("tools", create_tool_node_with_fallback(part_1_tools))
# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)
builder.add_edge("tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
part_1_graph = builder.compile(checkpointer=memory)

# Let's create an example conversation a user might have with the assistant
tutorial_questions = [
    # "I want to find a laptop. My budget is $1300. Can you help me find one?",
    # "Find me products under $500 in the electronics category",
    "I'm looking for Fitbit Charge 5. Are there any available?",
    "I want to find a laptop. My budget is $1300. Can you help me find one?",
    "Ok, I think I'll go with the Macbook Air. Can you add it to my cart?",
    "What items are in my shopping carts now?",
    "I'm ready to check out. Can you create an order for me?",


    # "What is the result of the 2024 U.S. presidential election?",
    # "Am i allowed to update my flight to something sooner? I want to leave later today.",
    # "Update my flight to sometime next week then",
    # "The next available option is great",
    # "what about lodging and transportation?",
    # "Yeah i think i'd like an affordable hotel for my week-long stay (7 days). And I'll want to rent a car.",
    # "OK could you place a reservation for your recommended hotel? It sounds nice.",
    # "yes go ahead and book anything that's moderate expense and has availability.",
    # "Now for a car, what are my options?",
    # "Awesome let's just get the cheapest option. Go ahead and book for 7 days",
    # "Cool so now what recommendations do you have on excursions?",
    # "Are they available while I'm there?",
    # "interesting - i like the museums, what options are there? ",
    # "OK great pick one and book it for my second day there.",
]

# Update with the backup file so we can restart from the original place in each section
# db = update_dates(db)
thread_id = str(uuid.uuid4())

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        "customer_id": "101",
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


_printed = set()
for question in tutorial_questions:
    events = part_1_graph.stream(
        {"messages": ("user", question)}, config, stream_mode="values"
    )
    for event in events:
        _print_event(event, _printed)