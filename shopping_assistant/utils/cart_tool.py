# tools/cart_tool.py

from langchain.agents import tool
import sqlite3

def add_to_cart(customer_id: int, product_id: int, quantity: int):
    '''
    Insert a new item into the cart_items table.
    Args:
        customer_id (int): The id of the customer.
        product_id (int): The id of the product.
        quantity (int): The quantity of the product.
    Returns:
        str: A message indicating the success of the operation.
    '''
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

def clear_cart(customer_id: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM cart_items WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()
    return "Cart cleared."

def num_of_item_in_cart(customer_id: int, product_id: int):
    """
    Retrieve the number of a specific item in a customer's cart.
    Args:
        customer_id (int): The ID of the customer.
        product_id (int): The ID of the product.
    Returns:
        int: The quantity of the specified product in the customer's cart. 
             Returns 0 if the product is not found in the cart.
    """
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cart_items WHERE customer_id = ? AND product_id = ?", (customer_id, product_id))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[3]
    else:
        return 0

def update_cart(customer_id: int, product_id: int, quantity: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE cart_items SET quantity = ? WHERE customer_id = ? AND product_id = ?",
                     (quantity, customer_id, product_id))
    conn.commit()
    conn.close()
    return f"Updated quantity of product {product_id} to {quantity}."

def remove_from_cart(customer_id: int, product_id: int, quantity: int = None):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    # Check if the item is in the cart.
    cursor.execute("SELECT * FROM cart_items WHERE customer_id = ? AND product_id = ?", (customer_id, product_id))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return "Item not found in cart."
    
    # If quantity is not specified, remove all of the item.
    if quantity is None:
        cursor.execute("DELETE FROM cart_items WHERE customer_id = ? AND product_id = ?", (customer_id, product_id))
        conn.commit()
        conn.close()
        return f"Removed all of product {product_id} from cart."
    else:
        current_quantity = result[3]
        # If the quantity to remove is greater than the current quantity, remove all of the item.
        if quantity >= current_quantity:
            cursor.execute("DELETE FROM cart_items WHERE customer_id = ? AND product_id = ?", (customer_id, product_id))
            conn.commit()
            conn.close()
            return f"The quantity to remove is greater than the current quantity. All of product {product_id} removed."

        else:
            cursor.execute("UPDATE cart_items SET quantity = quantity - ? WHERE customer_id = ? AND product_id = ?",
                           (quantity, customer_id, product_id))
            conn.commit()
            conn.close()
            return f"Removed {quantity} of product {product_id} from cart."
            
def search_items_in_cart(customer_id: int, name: str = None, category: str = None, type: str = None):
    '''
    Search for items in the cart of the current customer by name, category, and type.
    Args:
        customer_id (int): The id of the customer.
        name (str): The name of the product.
        category (str): The category of the product.
        type (str): The type of the product.
    Returns:
        list: A list of dictionaries containing the product name, price, and quantity.'''
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    sql_query = "SELECT p.id p.name, p.price, ci.quantity FROM cart_items ci JOIN products p ON ci.product_id = p.id WHERE ci.customer_id = ?"
    parameters = [customer_id]

    if name is not None:
        sql_query += " AND name LIKE ?"
        parameters.append(name)
    if category is not None:
        sql_query += " AND category LIKE ?"
        parameters.append(category)
    if type is not None:
        sql_query += " AND type LIKE ?"
        parameters.append(type)
    
    cursor.execute(sql_query, parameters)
    results = cursor.fetchall()
    conn.close()
    return results

# @tool
# def update_cart_tool(customer_id: int, product_id: int, quantity: int):
#     """
#     Tool to update the quantity of a product in the shopping cart.
#     """
#     return update_cart(customer_id, product_id, quantity)

@tool
def add_to_cart_tool(customer_id: int, product_id: int, quantity: int):
    """
    Tool to add an item with certain quantity to the shopping cart.
    Args:
        customer_id (int): The ID of the customer.
        product_id (int): The ID of the product.
        quantity (int): The quantity of the product.
    """
    num = num_of_item_in_cart(customer_id, product_id)
    if num == 0:
        return add_to_cart(customer_id, product_id, quantity)
    else:
        return update_cart(customer_id, product_id, num + quantity)

@tool
def fetch_cart_tool(customer_id: int):
    """
    Tool to fetch the shopping cart by customer id.
    """
    return fetch_cart(customer_id)

@tool
def clear_cart_tool(customer_id: int):
    """
    Tool to clear the shopping cart by customer id.
    """
    return clear_cart(customer_id)

@tool
def remove_from_cart_tool(customer_id: int, product_id: int, quantity: int = None):
    """
    Tool to remove an item from the shopping cart.
    Args:
        customer_id (int): The ID of the customer.
        product_id (int): The ID of the product.
        quantity (int): The quantity of the product to remove. If not specified, remove all of the item
    Returns:
        str: A message indicating the success of the operation.
    """
    return remove_from_cart(customer_id, product_id, quantity)


