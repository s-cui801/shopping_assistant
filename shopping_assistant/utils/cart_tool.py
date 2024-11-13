# tools/cart_tool.py

from langchain.agents import tool
import sqlite3
from shopping_assistant.models import CartItem, Product

def add_to_cart(customer_id: int, product_id: int, quantity: int):
    '''
    Insert a new item into the cart_items table using Django ORM.
    '''
    CartItem.objects.create(
        customer_id=customer_id,
        product_id=product_id,
        quantity=quantity
    )
    return f"Added {quantity} of product {product_id} to cart."

def fetch_cart(customer_id: int):
    cart_items = CartItem.objects.filter(customer_id=customer_id).select_related('product')
    return [(item.product.name, item.product.price, item.quantity) for item in cart_items]

def clear_cart(customer_id: int):
    CartItem.objects.filter(customer_id=customer_id).delete()
    return "Cart cleared."

def num_of_item_in_cart(customer_id: int, product_id: int):
    """
    Retrieve the number of a specific item in a customer's cart.
    """
    try:
        cart_item = CartItem.objects.get(customer_id=customer_id, product_id=product_id)
        return cart_item.quantity
    except CartItem.DoesNotExist:
        return 0

def update_cart(customer_id: int, product_id: int, quantity: int):
    CartItem.objects.filter(
        customer_id=customer_id, 
        product_id=product_id
    ).update(quantity=quantity)
    return f"Updated quantity of product {product_id} to {quantity}."

def remove_from_cart(customer_id: int, product_id: int, quantity: int = None):
    try:
        cart_item = CartItem.objects.get(customer_id=customer_id, product_id=product_id)
        if quantity is None or quantity >= cart_item.quantity:
            cart_item.delete()
            return f"Removed all of product {product_id} from cart."
        else:
            cart_item.quantity -= quantity
            cart_item.save()
            return f"Removed {quantity} of product {product_id} from cart."
    except CartItem.DoesNotExist:
        return "Item not found in cart."

def search_items_in_cart(customer_id: int, name: str = None, category: str = None, type: str = None):
    '''
    Search for items in the cart using Django ORM.
    '''
    query = CartItem.objects.filter(customer_id=customer_id).select_related('product')
    
    if name:
        query = query.filter(product__name__icontains=name)
    if category:
        query = query.filter(product__category__icontains=category)
    if type:
        query = query.filter(product__type__icontains=type)
    
    return [(item.product.id, item.product.name, item.product.price, item.quantity) 
            for item in query]

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


