# from langchain.agents import tool

# def check_discount(cart_total: float):
#     discount = 0
#     if cart_total > 100:
#         discount = 10  # For example, a 10% discount on orders over $100
#     return discount

# @tool
# def check_discount_tool(cart_total: float):
#     """
#     Tool to check policies, e.g., discounts.
#     """
#     return check_discount(cart_total)