# tools/cart_tool.py

from langchain.agents import tool
import sqlite3

def add_to_cart(customer_id: int, product_id: int, quantity: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = ?", (customer_id,))
    cart_id = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)", 
                   (cart_id, product_id, quantity))
    conn.commit()
    conn.close()
    return f"Added {quantity} of product {product_id} to cart."

def fetch_cart(customer_id: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT p.name, p.price, ci.quantity FROM shopping_cart sc JOIN cart_items ci ON sc.cart_id = ci.cart_id JOIN products p ON ci.product_id = p.id WHERE sc.customer_id = ?",
                   (customer_id,))

    results = cursor.fetchall()
    conn.close()
    return results

@tool
def add_to_cart_tool(customer_id: int, product_id: int, quantity: int):
    """
    Tool to add an item to the shopping cart.
    """
    return add_to_cart(customer_id, product_id, quantity)

@tool
def fetch_cart_tool(customer_id: int):
    """
    Tool to fetch the shopping cart by customer id.
    """
    return fetch_cart(customer_id)

def clear_cart(customer_id: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = ?", (customer_id,))
    cart_id = cursor.fetchone()[0]
    
    cursor.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
    conn.commit()
    conn.close()
    return "Cart cleared."