from langchain.agents import tool
import sqlite3
from datetime import datetime

def create_order(cart_id: int, total_amount: float):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    # Add the cart to oders
    cursor.execute("INSERT INTO orders (cart_id, order_status, payment_status, order_date) VALUES (?, ?, ?, ?)", 
                   (cart_id, "Pending", "Unpaid", datetime.now()))
    
    conn.commit()
    conn.close()

    return "Order created successfully."

@tool
def create_order_tool(customer_id: int, total_amount: float):
    """
    Tool to create a new order.
    """
    return create_order(customer_id, total_amount)