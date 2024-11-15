# tools/products_tool.py
from langchain.agents import tool
import sqlite3
from ..models import Products
from django.db.models import Q

def search_products(name: str = None, category: str = None, type: str = None, description: str = None, 
                   min_price: float = None, max_price: float = None, is_category: bool = False, is_type: bool = False):
    # Start with all products
    queryset = Products.objects.all()

    # Decide whether the query is a category or name
    if not (is_category or is_type):
        if description:
            # Split description into words and create Q objects for OR conditions
            description_words = description.split()
            description_query = Q()
            for word in description_words:
                description_query |= Q(description__icontains=word)
            queryset = queryset.filter(description_query)

    if name:
        queryset = queryset.filter(name__icontains=name)
    
    if min_price is not None:
        queryset = queryset.filter(price__gte=min_price)

    if max_price is not None:
        queryset = queryset.filter(price__lte=max_price)
    
    if type:
        queryset = queryset.filter(type__icontains=type)
    
    if category:
        queryset = queryset.filter(category__icontains=category)

    # Convert queryset to list of dictionaries
    return [
        {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "category": product.category,
            "type": product.type,
            "description": product.description
        }
        for product in queryset
    ]

def get_product_by_product_id(product_id: int):
    try:
        product = Products.objects.get(product_id=product_id)
        return {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "stock": product.stock,
            "category": product.category,
            "type": product.type,
            "description": product.description
        }
    except Products.DoesNotExist:
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

