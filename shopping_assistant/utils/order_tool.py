from langchain.agents import tool
import sqlite3
from datetime import datetime
from shopping_assistant.models import Order

def create_order(cart_id: int, total_amount: float):
    order = Order.objects.create(
        cart_id=cart_id,
        order_status="Pending",
        payment_status="Unpaid",
        order_date=datetime.now()
    )
    return "Order created successfully."

@tool
def create_order_tool(customer_id: int, total_amount: float):
    """
    Tool to create a new order.
    """
    return create_order(customer_id, total_amount)