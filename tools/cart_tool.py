# tools/cart_tool.py

from langchain.agents import tool
import sqlite3

def add_to_cart(customer_id: int, product_id: int, quantity: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    # cursor.execute("SELECT cart_id FROM shopping_cart WHERE customer_id = ?", (customer_id,))
    # cart_id = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO cart_items (customer_id, product_id, quantity) VALUES (?, ?, ?)", 
                   (customer_id, product_id, quantity))
    conn.commit()
    conn.close()
    return f"Added {quantity} of product {product_id} to cart."

def fetch_cart(customer_id: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT p.name, p.price, ci.quantity FROM cart_items ci JOIN products p ON ci.product_id = p.id WHERE ci.customer_id = ?",
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
    
    cursor.execute("DELETE FROM cart_items WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()
    return "Cart cleared."

@tool
def clear_cart_tool(customer_id: int):
    """
    Tool to clear the shopping cart by customer id.
    """
    return clear_cart(customer_id)

def update_cart(customer_id: int, product_id: int, quantity: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE cart_items SET quantity = ? WHERE customer_id = ? AND product_id = ?",
                     (quantity, customer_id, product_id))
    conn.commit()
    conn.close()
    return f"Updated quantity of product {product_id} to {quantity}."

@tool
def update_cart_tool(customer_id: int, product_id: int, quantity: int):
    """
    Tool to update the quantity of a product in the shopping cart.
    """
    return update_cart(customer_id, product_id, quantity)

