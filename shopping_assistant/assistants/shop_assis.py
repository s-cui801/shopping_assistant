import os
from typing import Annotated
from datetime import datetime
import uuid

# from typing_extensions import TypedDict

# from langgraph.graph.message import AnyMessage, add_messages
# from langchain_core.messages import ToolMessage

# # from langchain_anthropic import ChatAnthropic
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import Runnable, RunnableConfig

# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.graph import END, StateGraph, START
# from langgraph.prebuilt import tools_condition
from ..utils.utilities import _store_event, _store_ai_messages

# from langchain_openai import ChatOpenAI

# from utils.products_tool import search_product_tool, search_products_recommendations_tool, get_product_by_product_id_tool
# from utils.cart_tool import fetch_cart_tool, add_to_cart_tool, clear_cart_tool, remove_from_cart_tool
# from utils.order_tool import create_order_tool
# from utils.policy_tool import check_discount_tool

from ..assistants.assistant_prompt import primary_assistant_prompt

from ..assistants.assistant_routing import shopping_assistant_graph


# class State(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]
#     customer_id: str

# class Assistant:
#     def __init__(self, runnable: Runnable):
#         self.runnable = runnable

#     def __call__(self, state: State, config: RunnableConfig):
#         while True:
#             configuration = config.get("configurable", {})
#             customer_id = configuration.get("customer_id", None)
#             state = {**state, "customer_id": customer_id}
#             result = self.runnable.invoke(state)
#             # If the LLM happens to return an empty response, we will re-prompt it
#             # for an actual response.
#             if not result.tool_calls and (
#                 not result.content
#                 or isinstance(result.content, list)
#                 and not result.content[0].get("text")
#             ):
#                 messages = state["messages"] + [("user", "Respond with a real output.")]
#                 state = {**state, "messages": messages}
#             else:
#                 break
#         return {"messages": result}


# llm = ChatOpenAI(model="gpt-4-turbo-preview")

# # primary_assistant_prompt = ChatPromptTemplate.from_messages(
# #     [
# #         (
# #             "system",
# #             "You are a helpful shopping assistant. "
# #             " Use the provided tools to search for products, shopping cart items, order statuses, policies and other information to assist the user's queries. "
# #             " When searching, be persistent. Expand your query bounds if the first search returns no results. "
# #             " If a search comes up empty, expand your search before giving up."
# #             " When searching, you are strictly limited to the database provided. "
# #             " When providing product categories, strictly use one of the following categories: 'Laptop', 'Smartphone', 'Headphones', 'Accessories', 'Wearables'. For example, if the user asks for 'Laptops', please respond with 'Laptop'."
# #             " When providing product types, strictly use one of the following types: 'Budget Laptop', 'Premium Laptop', 'Convertible Laptop', 'Flagship Smartphone', 'Mid-range Smartphone', 'Noise-cancelling Headphones', 'Portable Charger', 'Wireless Mouse', 'Fitness Tracker'. For example, if the user asks for 'Budget Smartphones', please respond with 'Budget Smartphone'."
# #             "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
# #             "\nCurrent time: {time}.",
# #         ),
# #         ("placeholder", "{messages}"),
# #     ]
# # ).partial(time=datetime.now)

# def create_shopping_assistant_graph(State, Assistant, llm):
#     safe_tools = [
#     TavilySearchResults(max_results=2),
#     search_product_tool,
#     search_products_recommendations_tool,
#     get_product_by_product_id_tool,
#     fetch_cart_tool,
#     # check_discount_tool,
# ]

#     sensitive_tools = [
#     add_to_cart_tool,
#     clear_cart_tool,
#     remove_from_cart_tool,
#     create_order_tool,
# ]
#     sensitive_tool_names = {t.name for t in sensitive_tools}


#     assistant_runnable = primary_assistant_prompt | llm.bind_tools(safe_tools + sensitive_tools)

# # Create the graph
#     builder = StateGraph(State)


# # Define nodes: these do the work
#     builder.add_node("assistant", Assistant(assistant_runnable))
#     builder.add_node("safe_tools", create_tool_node_with_fallback(safe_tools))
#     builder.add_node("sensitive_tools", create_tool_node_with_fallback(sensitive_tools))
# # Define edges: these determine how the control flow moves
#     builder.add_edge(START, "assistant")
# # builder.add_conditional_edges(
# #     "assistant",
# #     tools_condition,
# # )
# # builder.add_edge("tools", "assistant")

# # Create our own rule of routing instead of using the default `tools_condition`
#     def route_tools(state: State):
#         next_node = tools_condition(state)
#     # If no tools are invoked, return to the user
#         if next_node == END:
#             return END
    
#         ai_message = state["messages"][-1]
    
#     # Assume parallel tool calls by iterating through all tool calls in ai_message
#         sensitive_tool_used = any(
#         tool_call["name"] in sensitive_tool_names for tool_call in ai_message.tool_calls
#     )
    
#     # If any sensitive tool was called, route to "sensitive_tools"
#         if sensitive_tool_used:
#             return "sensitive_tools"
    
#     # Otherwise, route to "safe_tools"
#         return "safe_tools"

# # Add the conditional edges
#     builder.add_conditional_edges(
#     "assistant", route_tools, ["safe_tools", "sensitive_tools", END]
# )
#     builder.add_edge("safe_tools", "assistant")
#     builder.add_edge("sensitive_tools", "assistant")

# # The checkpointer lets the graph persist its state
# # this is a complete memory for the entire graph.
#     memory = MemorySaver()
#     shopping_assistant_graph = builder.compile(
#     checkpointer=memory,
#     interrupt_before=["sensitive_tools"])
        
#     return shopping_assistant_graph

# shopping_assistant_graph = create_shopping_assistant_graph(State, Assistant, llm)

# # Let's create an example conversation a user might have with the assistant
# tutorial_questions = [
#     # "I want to find a laptop. My budget is $1300. Can you help me find one?",
#     # "Find me products under $500 in the electronics category",
#     "I'm looking for Fitbit Charge 5. Are there any available?",
#     "I want to find a laptop. My budget is $1300. Can you help me find one?",
#     "Ok, I think I'll go with the Macbook Air. Can you add it to my cart?",
#     "Yes, I'd like to add 2 of the Macbook Air to my cart.",
#     "What items are in my shopping carts now?",
#     "Awesome. Can you remove one Dell XPS 13 from my cart?",
#     "Yes, I want to remove one Dell XPS 13 from my cart.",
#     "Now what's in my cart?",
#     "Can you recommend a good headphone with noise-cancelling feature?",
# ]

# Update with the backup file so we can restart from the original place in each section
# db = update_dates(db)
# thread_id = str(uuid.uuid4())

# config = {
#     "configurable": {
#         # The passenger_id is used in our flight tools to
#         # fetch the user's flight information
#         "customer_id": "1",
#         # Checkpoints are accessed by thread_id
#         "thread_id": thread_id,
#     }
# }


def stream_user_queries(shopping_assistant_graph, config, question):
    _printed = set()
    message_str = ""

    events = shopping_assistant_graph.stream(
    {"messages": ("user", question)}, config, stream_mode="values"
    )
    for event in events:
        # _store_event(event, message_list, _printed)
        message_str += _store_ai_messages(event, _printed)
    return message_str
    # snapshot = shopping_assistant_graph.get_state(config)
    # while snapshot.next:
    # # We have an interrupt! The agent is trying to use a tool, and the user can approve or deny it
    # # Note: This code is all outside of your graph. Typically, you would stream the output to a UI.
    # # Then, you would have the frontend trigger a new run via an API call when the user has provided input.
    #     try:
    #         user_input = input(
    #         "Do you approve of the above actions? Type 'y' to continue;"
    #         " otherwise, explain your requested changed.\n\n"
    #     )
    #     except:
    #         user_input = "y"
    #     if user_input.strip() == "y":
    #     # Just continue
    #         result = shopping_assistant_graph.invoke(
    #         None,
    #         config,
    #     )
    #     else:
    #     # Satisfy the tool invocation by
    #     # providing instructions on the requested changes / change of mind
        #     result = shopping_assistant_graph.invoke(
        #     {
        #         "messages": [
        #             ToolMessage(
        #                 tool_call_id=event["messages"][-1].tool_calls[0]["id"],
        #                 content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
        #             )
        #         ]
        #     },
        #     config,
        # )
    #     snapshot = shopping_assistant_graph.get_state(config)

# stream_user_queries(shopping_assistant_graph, config)
# for question in tutorial_questions:
#     events = shopping_assistant_graph.stream(
#         {"messages": ("user", question)}, config, stream_mode="values"
#     )
#     for event in events:
#         _print_event(event, _printed)
#     snapshot = shopping_assistant_graph.get_state(config)
#     while snapshot.next:
#         # We have an interrupt! The agent is trying to use a tool, and the user can approve or deny it
#         # Note: This code is all outside of your graph. Typically, you would stream the output to a UI.
#         # Then, you would have the frontend trigger a new run via an API call when the user has provided input.
#         try:
#             user_input = input(
#                 "Do you approve of the above actions? Type 'y' to continue;"
#                 " otherwise, explain your requested changed.\n\n"
#             )
#         except:
#             user_input = "y"
#         if user_input.strip() == "y":
#             # Just continue
#             result = shopping_assistant_graph.invoke(
#                 None,
#                 config,
#             )
#         else:
#             # Satisfy the tool invocation by
#             # providing instructions on the requested changes / change of mind
#             result = shopping_assistant_graph.invoke(
#                 {
#                     "messages": [
#                         ToolMessage(
#                             tool_call_id=event["messages"][-1].tool_calls[0]["id"],
#                             content=f"API call denied by user. Reasoning: '{user_input}'. Continue assisting, accounting for the user's input.",
#                         )
#                     ]
#                 },
#                 config,
#             )
#         snapshot = shopping_assistant_graph.get_state(config)