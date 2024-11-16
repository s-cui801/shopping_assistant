import os
from typing import Annotated
from datetime import datetime
import uuid

from ..utils.utilities import _store_event, _store_ai_messages

from ..assistants.assistant_prompt import primary_assistant_prompt
from ..assistants.assistant_routing import shopping_assistant_graph


def stream_user_queries(shopping_assistant_graph, config, question):
    '''
    Stream user queries to the shopping assistant graph, and return the assistant's response in a string format.
    Args:
        shopping_assistant_graph (StateGraph): The shopping assistant graph.
        config (RunnableConfig): The configuration for the assistant.
        question (str): The user's query.
    Returns:
        message_str: The assistant's response in a string format.
    '''
    _printed = set()
    message_str = ""

    events = shopping_assistant_graph.stream(
    {"messages": ("user", question)}, config, stream_mode="values"
    )
    for event in events:
        # _store_event(event, message_list, _printed)
        message_str += _store_ai_messages(event, _printed)
    return message_str