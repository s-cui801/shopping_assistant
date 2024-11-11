# tools/products_tool.py
from langchain.agents import tool
import sqlite3

def search_products(name: str = None, category: str = None, type: str = None, description: str = None, min_price: float = None, max_price: float = None, is_category: bool = False, is_type: bool = False):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    # Start the base query
    sql_query = "SELECT * FROM products WHERE 1=1"
    parameters = []

    # Decide whether the query is a category or name
    if not (is_category or is_type):
        # If it's not a category, search in the name and description
        if description:
            # Separate the query by spaces and search for each word in the name and description
            description = description.split()
            for word in description:
                sql_query += " OR description LIKE ?"
                parameters.append(f"%{word}%")
    if name:
        sql_query += " AND name LIKE ?"
        parameters.append(f"%{name}%")
    
    # Add price filters if they are set
    if min_price is not None:
        sql_query += " AND price >= ?"
        parameters.append(min_price)

    if max_price is not None:
        sql_query += " AND price <= ?"
        parameters.append(max_price)
    
    if type:
        sql_query += " AND type LIKE ?"
        parameters.append(f"%{type}%")
    
    if category:
        sql_query += " AND category LIKE ?"
        parameters.append(f"%{category}%")

    cursor.execute(sql_query, parameters)
    results = cursor.fetchall()
    conn.close()

    # Return the results as a list of dictionaries
    return [{"product_id": row[0], "name": row[1], "price": row[2], "stock": row[3], "category": row[4], "type": row[5], "description": row[6]} for row in results]

def get_product_by_product_id(product_id: int):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {"product_id": result[0], "name": result[1], "price": result[2], "stock": result[3], "category": result[4], "type": result[5], "description": result[6]}
    else:
        return None

@tool
def search_product_tool(name: str = None, category: str = None, type: str = None, description: str = None, min_price: float = None, max_price: float = None, is_category: bool = False):
    """ 
    Tool to search all the information for products in the database. 
    Args: 
        query (str): The search query.
        category (str): The category of the product.
        type (str): The type of the product.
        min_price (float): The minimum price of the product.
        max_price (float): The maximum price of the product.
        is_category (bool): Whether the query is a category or not.
    Returns:
        list: A list of dictionaries containing the product information.
        If no products are found, return None.
    """
    return search_products(name, category, type, description, min_price, max_price, is_category)

@tool
def get_product_by_product_id_tool(product_id: int):
    """ Tool to get a product by its ID. """
    return get_product_by_product_id(product_id)

@tool

def search_products_recommendations_tool(name: str = None, category: str = None, type: str = None, description: str = None, min_price: float = None, max_price: float = None, is_category: bool = False):
    """ 
    Tool to search for product recommendations based on the provided criteria.
    Args:
        name (str, optional): The name of the product.
        category (str, optional): The category of the product.
        type (str, optional): The type of the product.
        description (str, optional): The description of the product.
        min_price (float, optional): The minimum price of the product.
        max_price (float, optional): The maximum price of the product.
        is_category (bool, optional): Whether the query is a category or not.

    If no products are found, returns an empty list.
    """
    return search_products(name, category, type, description, min_price, max_price, is_category)

