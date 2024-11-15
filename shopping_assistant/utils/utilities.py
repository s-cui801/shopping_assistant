from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.runnables import RunnableLambda

from langgraph.prebuilt import ToolNode


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)

def _store_event(event: dict, stored_messages: list, _printed: set, max_length=1500):
    """
    Store event messages in a list instead of printing them.
    
    Args:
        event (dict): Event containing messages and dialog state
        stored_messages (list): List to store messages
        max_length (int): Maximum length for message content
        
    Returns:
        list: Updated stored_messages list
    """
    current_state = event.get("dialog_state")
    if current_state:
        stored_messages.append(f"Currently in: {current_state[-1]}")
    
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            stored_messages.append(msg_repr)
            _printed.add(message.id)

def _store_ai_messages(event: dict, stored_messages: list, _printed: set, max_length=1500):
    """
    Store only AI messages in a list.
    
    Args:
        event (dict): Event containing messages
        stored_messages (list): List to store AI messages
        _printed (set): Set to track processed message IDs
        max_length (int): Maximum length for message content
        
    Returns:
        list: Updated stored_messages list
    """
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
            
        # Only process AI messages
        if isinstance(message, AIMessage):
            if message.id not in _printed:
                # msg_repr = message.pretty_repr(html=True)
                msg_repr = message.content
                if len(msg_repr) > max_length:
                    msg_repr = msg_repr[:max_length] + " ... (truncated)"
                stored_messages.append(msg_repr)
                _printed.add(message.id)
    
    return stored_messages
    