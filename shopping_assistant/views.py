from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db import connection
from django.contrib.auth import login as django_login
from django.urls import reverse
from .forms import CustomerRegistrationForm
from .models import Customers

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
    # Get customer_id from URL parameters
    customer_id = request.GET.get('customer_id', None)

    # Initialize conversation history (this could be stored in the session for persistence)
    if 'conversation' not in request.session:
        request.session['conversation'] = []

    # Process user input and get the assistant's response
    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')
        
        if user_message:
            # Append user message to the conversation history
            request.session['conversation'].append({'role': 'user', 'content': user_message})
            
            # Get the assistant's response (implement this logic based on your AI assistant model)
            # assistant_response = process_user_message(user_message, customer_id)
            assistant_response = "This is a placeholder response from the assistant."

            # Append assistant's response to the conversation history
            request.session['conversation'].append({'role': 'assistant', 'content': assistant_response})

            request.session.modified = True

            # Return a JSON response with the conversation
            return JsonResponse({'messages': request.session['conversation']})

    # Render the assistant page with the conversation history
    return render(request, 'assistant_page.html', {
        'conversation': request.session['conversation'],
        'customer_id': customer_id,
    })
