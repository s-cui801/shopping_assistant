from langchain.agents import tool
import sqlite3
from datetime import datetime
from shopping_assistant.models import Orders, OrderItems, Products

# def create_order(cart_id: int, total_amount: float):
#     order = Orders.objects.create(
#         cart_id=cart_id,
#         order_status="Pending",
#         payment_status="Unpaid",
#         order_date=datetime.now()
#     )
#     return "Order created successfully."

def search_order_by_customer_id(customer_id: int):
    orders = Orders.objects.filter(customer_id=customer_id)
    return [
        {
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "order_status": order.order_status,
            "payment_status": order.payment_status,
            "order_date": order.order_date,
        }
        for order in orders
    ]

def search_order_info_by_order_id(order_id: int):
    order_info = OrderItems.objects.filter(order_id=order_id).select_related('product')
    return [(item.product.name, item.product.price, item.quantity) for item in order_info]

@tool
def search_order_by_customer_id_tool(customer_id: int):
    """
    Tool to search orders by customer id. Help user track their orders.
    """
    return search_order_by_customer_id(customer_id)

# @tool
# def create_order_tool(customer_id: int, total_amount: float):
#     """
#     Tool to create a new order.
#     """
#     return create_order(customer_id, total_amount)

@tool
def search_order_info_by_order_id_tool(order_id: int):
    """
    Tool to search order items by order id.
    """
    return search_order_info_by_order_id(order_id)

delivery_queries = {
    "delivery_time_estimate": "Your order is expected to arrive within 3-5 business days. For express shipping, it may arrive in 1-2 business days. You can track your order in the 'My Orders' section.",
    "expedited_shipping": "Yes, we offer expedited shipping options. During checkout, you can choose 'Express Shipping' to receive your order faster."
}

payment_queries = {
    "cash_on_delivery": "Cash on delivery is available in select regions. Please check during checkout to see if this option is available for your location.",
    "credit_card": "We accept all major credit cards including Visa, MasterCard, and American Express. Enter your card details at checkout to complete the payment.",
    "digital_wallets": "We support payments through popular digital wallets like PayPal, Apple Pay, and Google Pay for your convenience.",
    "gift_cards": "You can redeem gift cards during checkout by entering the gift card code in the designated field.",
    "installment_plans": "Installment payment options are available for select purchases. Choose this option at checkout to split your payment into manageable monthly amounts.",
    "discounts_and_promotions": "We frequently offer discounts and promotions. Please check our 'Offers' page or subscribe to our newsletter to stay updated on the latest deals.",
    "payment_security": "All transactions are secured with SSL encryption to ensure your payment details are protected.",
    "currency_support": "We accept payments in multiple currencies. During checkout, the total amount will be displayed in your local currency if supported.",
    "payment_methods": "We accept a variety of payment methods including credit/debit cards, digital wallets (e.g., PayPal, Apple Pay, Google Pay), bank transfers, and gift cards. Please select your preferred method during checkout."
}

checkout_queries = {
    "checkout_procedure": "To proceed to checkout, please review the items in your cart and click the 'Checkout' button. You’ll then be guided through the payment and delivery details."
}

order_queries = {
    "order_tracking": "You can track your order in real-time under the 'My Orders' section. Please enter your order ID for detailed updates.",
    "order_delay": "We’re sorry for the delay. Please check the order tracking information for updates. If you need further assistance, contact our support team.",
    "order_modification": "You can change your order within 30 minutes of placing it. Go to 'My Orders' and select 'Modify Order'. For assistance, reach out to customer support."
}

policy_queries = {
    "refund_policy": "We offer a full refund for returns made within 30 days of delivery, provided the items are unused and in their original packaging."
}

@tool
def delivery_query_tool():
    """Get predefined delivery-related queries and responses.
    
    Returns:
        dict: Mapping of delivery questions to corresponding answers about 
        shipping methods, delivery times, and tracking information.
    """
    return delivery_queries

@tool
def payment_query_tool():
    """Get predefined payment-related queries and responses.
    
    Returns:
        dict: Mapping of payment questions to corresponding answers about
        payment methods, refunds, and billing issues.
    """
    return payment_queries

@tool
def checkout_query_tool():
    """Get predefined checkout-related queries and responses.
    
    Returns:
        dict: Mapping of checkout questions to corresponding answers about
        order completion, cart issues, and purchase confirmation.
    """
    return checkout_queries

@tool
def order_query_tool():
    """Get predefined order-policy-related queries and responses.
    
    Returns:
        dict: Mapping of order questions to corresponding answers about
        order delay, modifications, and cancellations.
    """
    return order_queries

@tool
def policy_query_tool():
    """Get predefined policy-related queries and responses.
    
    Returns:
        dict: Mapping of policy questions to corresponding answers about
        return policies, warranties, and terms of service.
    """
    return policy_queries
