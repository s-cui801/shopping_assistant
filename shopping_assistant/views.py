from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db import connection
from django.contrib.auth import login as django_login

# Create your views here.
def hello_world(request):
    return HttpResponse("Hello world!")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Execute the raw SQL query to authenticate user
        cursor = connection.cursor()
        query = "SELECT * FROM customers WHERE username = %s AND password = %s"
        cursor.execute(query, [username, password])
        user = cursor.fetchone()  # Fetch one user, or None if not found

        if user:
            # If user found, start a session and log them in
            request.session['customer_id'] = user[0]  # Assuming user[0] is the user_id or primary key
            return redirect('assistant_page')  # Redirect to the shopping assistant page after login
        else:
            messages.error(request, 'Invalid credentials, please try again.')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']

        # Execute the raw SQL query to create a new user
        cursor = connection.cursor()
        query = "INSERT INTO customers (first_name, last_name, username, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, [first_name, last_name, username, password])

        messages.success(request, 'User registered successfully! Please log in.')
        return redirect('login')

    return render(request, 'register.html')

def assistant_page(request):
    return render(request, 'assistant_page.html')