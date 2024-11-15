from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db import connection
from django.contrib.auth import login as django_login
from django.urls import reverse
import uuid
from .forms import CustomerRegistrationForm
from .models import Customers
from .assistants.shop_assis import stream_user_queries, shopping_assistant_graph
from langchain_core.messages import ToolMessage
from django.http import StreamingHttpResponse
from django.shortcuts import render
import time

# Create your views here.
def hello_world(request):
    return HttpResponse("Hello world!")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            customer = Customers.objects.get(username=username, password=password)
            request.session['customer_id'] = customer.customer_id
            return redirect(reverse('assistant') + f"?customer_id={customer.customer_id}")
        except Customers.DoesNotExist:
            messages.error(request, 'Invalid credentials, please try again.')
            
    return render(request, 'login.html')

# def register_view(request):
#     if request.method == 'POST':
#         first_name = request.POST['first_name']
#         last_name = request.POST['last_name']
#         username = request.POST['username']
#         password = request.POST['password']

#         # Execute the raw SQL query to create a new user
#         cursor = connection.cursor()
#         query = "INSERT INTO customers (first_name, last_name, username, password) VALUES (%s, %s, %s, %s)"
#         cursor.execute(query, [first_name, last_name, username, password])

#         messages.success(request, 'User registered successfully! Please log in.')
#         return redirect('login')

#     return render(request, 'register.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            
            # Save password as plaintext (for quick prototyping only!)
            customer.password = form.cleaned_data['password']
            customer.save()
            
            return redirect(reverse('assistant') + f"?customer_id={customer.customer_id}")
    else:
        form = CustomerRegistrationForm()

    return render(request, 'register.html', {'form': form})

# def assistant_view(request):
#     customer_id = request.GET.get('customer_id')
#     if customer_id:
#         customer = Customers.objects.get(customer_id=customer_id)
#         return HttpResponse(f"Welcome to the assistant page, {customer.first_name}!")
#     else:
#         return HttpResponse("Error: Customer ID not found.")
def assistant_view(request):
    # def event_stream():
    #     config = request.session['config']
    #     snapshot = shopping_assistant_graph.get_state(config)
    #     while snapshot.next:
    #         yield f"data: Do you confirm the action? Type 'y' to continue.\n\n"
    #         time.sleep(1)  # Wait a moment before checking for a response
    #         if request.method == 'POST':
    #             user_message = request.POST.get('user_message', '')
    #             if user_message == 'y':
    #                 result = shopping_assistant_graph.invoke(
    #                 None,
    #                 config,
    #                 )
    #                 yield f"data: Action confirmed, proceeding...\n\n"
    #             else:
    #                 result = shopping_assistant_graph.invoke(
    #                     {
    #                         "messages": [
    #                             ToolMessage(
    #                                 tool_call_id=snapshot.messages[-1].tool_calls[0]["id"],
    #                                 content=f"API call denied by user. Reasoning: '{user_message}'. Continue assisting, accounting for the user's input.",
    #                             )
    #                         ]
    #                     },
    #                     config,
    #                 )
    #                 yield f"data: Action cancelled.\n\n"
    #         snapshot = shopping_assistant_graph.get_state(config)


    # Get customer_id from URL parameters
    customer_id = request.GET.get('customer_id', None)

    # Initialize conversation history (this could be stored in the session for persistence)
    if 'conversation' not in request.session:
        request.session['conversation'] = []
    
    # Initialize the config for the user queries
    if 'config' not in request.session:
        request.session['config'] = {
            "configurable": {
                "customer_id": str(customer_id),
                # Checkpoints are accessed by thread_id
                "thread_id": str(uuid.uuid4()),
            }
        }
    
    config = request.session['config']
    
    if 'need_confirmation' not in request.session:
        request.session['need_confirmation'] = False

    # Process user input and get the assistant's response
    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')
        
        if user_message and request.session['need_confirmation'] == False: # If the user don't need to confirm the action
            # Append user message to the conversation history
            request.session['conversation'].append({'role': 'user', 'content': user_message})
            
            # Get the assistant's response (implement this logic based on your AI assistant model)
            # assistant_response = process_user_message(user_message, customer_id)
            assistant_response_list = stream_user_queries(shopping_assistant_graph, request.session['config'], user_message)

            snapshot = shopping_assistant_graph.get_state(request.session['config'])
            if snapshot.next:
                request.session['need_confirmation'] = True
                assistant_response_list.append('Do you confirm the action? Type "y" to continue.')
            
                # Append assistant's response to the conversation history
            request.session['conversation'].append({'role': 'assistant', 'content': assistant_response_list})

            request.session.modified = True

                # Return a JSON response with the conversation
            return JsonResponse({'messages': request.session['conversation'], 'need_confirmation': request.session['need_confirmation']})
        elif user_message and request.session['need_confirmation'] == True: # If the user need to confirm the action
            if user_message == 'y':
                request.session['conversation'].append({'role': 'user', 'content': user_message})
                result = shopping_assistant_graph.invoke(
                    None,
                    config,
                )
                assistant_response = "Action confirmed and executed successfully."
                request.session['conversation'].append({'role': 'assistant', 'content': [assistant_response]})
                request.session['need_confirmation'] = False
            else:
                request.session['conversation'].append({'role': 'user', 'content': user_message})
                result = shopping_assistant_graph.invoke(
                    {
                        "messages": [
                            ToolMessage(
                                tool_call_id=snapshot.messages[-1].tool_calls[0]["id"],
                                content=f"API call denied by user. Reasoning: '{user_message}'. Continue assisting, accounting for the user's input.",
                            )
                        ]
                    },
                    config,
                )
                assistant_response = "Action cancelled. How else can I help you?"
                request.session['conversation'].append({'role': 'assistant', 'content': [assistant_response]})
                request.session['need_confirmation'] = False
            request.session.modified = True
            return JsonResponse({'messages': request.session['conversation'], 'need_confirmation': request.session['need_confirmation']})

    # Render the assistant page with the conversation history
    return render(request, 'assistant_page.html', {
        'conversation': request.session['conversation'],
        'customer_id': customer_id,
        'config': request.session['config'],
        'need_confirmation': request.session['need_confirmation']
    })
