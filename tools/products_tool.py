# tools/products_tool.py
from langchain.agents import tool
import sqlite3

def search_products(query: str = None, category: str = None, type: str = None, min_price: float = None, max_price: float = None, is_category: bool = False):
    conn = sqlite3.connect('shopping_assistant.db')
    cursor = conn.cursor()

    # Start the base query
    sql_query = "SELECT * FROM products WHERE 1=1"
    parameters = []

    # Decide whether the query is a category or name
    if is_category:
        sql_query += " AND category LIKE ?"
        parameters.append(f"%{query}%")
    else:
        # If it's not a category, search in the name and description
        if query:
            sql_query += " AND name LIKE ?"
            parameters.append(f"%{query}%")
            sql_query += " OR description LIKE ?"
            parameters.append(f"%{query}%")
    
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

@tool
def search_product_tool(query: str = None, category: str = None, type: str = None, min_price: float = None, max_price: float = None, is_category: bool = False):
    """ Tool to search for products in the database. """
    return search_products(query, category, type, min_price, max_price, is_category)

def get_product(product_id: int):
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
def get_product_tool(product_id: int):
    """ Tool to get a product by its ID. """
    return get_product(product_id)

