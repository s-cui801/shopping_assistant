from ..models import Customers
from langchain.agents import tool


def fetch_customer_information(customer_id: int):
    """
    Tool to fetch the customer information by customer id.
    """
    try:
        customer = Customers.objects.get(customer_id=customer_id)
        return {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "username": customer.username,
        }
    except Customers.DoesNotExist:
        return None

@tool
def fetch_customer_information_tool(customer_id: int):
    """
    Tool to fetch the customer information by customer id.
    """
    return fetch_customer_information(customer_id)