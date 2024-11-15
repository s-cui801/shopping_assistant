from langgraph.graph import StateGraph
from langchain_community.tools import TavilySearchResults

from ..utils.products_tool import search_product_tool, search_products_recommendations_tool, get_product_by_product_id_tool
from ..utils.cart_tool import fetch_cart_tool, add_to_cart_tool, clear_cart_tool, remove_from_cart_tool
from ..utils.order_tool import search_order_by_customer_id_tool, search_order_info_by_order_id_tool, payment_query_tool, policy_query_tool, delivery_query_tool, order_query_tool, checkout_query_tool
from ..utils.customer_tool import fetch_customer_information_tool

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from ..utils.utilities import create_tool_node_with_fallback

from ..assistants.assistant_core import Assistant, State, llm
from ..assistants.assistant_prompt import primary_assistant_prompt



safe_tools = [
    TavilySearchResults(max_results=2),
    search_product_tool,
    search_products_recommendations_tool,
    get_product_by_product_id_tool,
    fetch_cart_tool,
    fetch_customer_information_tool,
    search_order_by_customer_id_tool,
    search_order_info_by_order_id_tool,
    payment_query_tool, 
    policy_query_tool, 
    delivery_query_tool, 
    order_query_tool, 
    checkout_query_tool,
    # check_discount_tool,
]

sensitive_tools = [
add_to_cart_tool,
clear_cart_tool,
remove_from_cart_tool,

]
sensitive_tool_names = {t.name for t in sensitive_tools}


assistant_runnable = primary_assistant_prompt | llm.bind_tools(safe_tools + sensitive_tools)

# Create the graph
builder = StateGraph(State)

# def customer_info(state: State):
#     return {"customer_info": fetch_customer_information_tool.invoke({})}

# Define nodes: these do the work
# builder.add_node("fetch_customer_info", customer_info)
builder.add_node("assistant", Assistant(assistant_runnable))
builder.add_node("safe_tools", create_tool_node_with_fallback(safe_tools))
builder.add_node("sensitive_tools", create_tool_node_with_fallback(sensitive_tools))
# Define edges: these determine how the control flow moves
# builder.add_edge(START, "fetch_customer_info")
# builder.add_edge("fetch_customer_info", "assistant")
builder.add_edge(START, "assistant")
# builder.add_conditional_edges(
#     "assistant",
#     tools_condition,
# )
# builder.add_edge("tools", "assistant")

# Create our own rule of routing instead of using the default `tools_condition`
def route_tools(state: State):
    next_node = tools_condition(state)
# If no tools are invoked, return to the user
    if next_node == END:
        return END

    ai_message = state["messages"][-1]

# Assume parallel tool calls by iterating through all tool calls in ai_message
    sensitive_tool_used = any(
    tool_call["name"] in sensitive_tool_names for tool_call in ai_message.tool_calls
)

# If any sensitive tool was called, route to "sensitive_tools"
    if sensitive_tool_used:
        return "sensitive_tools"

# Otherwise, route to "safe_tools"
    return "safe_tools"

# Add the conditional edges
builder.add_conditional_edges(
"assistant", route_tools, ["safe_tools", "sensitive_tools", END]
)
builder.add_edge("safe_tools", "assistant")
builder.add_edge("sensitive_tools", "assistant")

# The checkpointer lets the graph persist its state
# this is a complete memory for the entire graph.
memory = MemorySaver()
shopping_assistant_graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["sensitive_tools"]
)