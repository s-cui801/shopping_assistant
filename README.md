# Shopping Assistant - README

## Setup Instructions

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/s-cui801/shopping_assistant
    cd shopping-assistant
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables:**
    - Create a `.env` file in the project root directory.
    - Add the following variables:
      ```plaintext
      OPENAI_API_KEY=<your_openai_api_key>
      TAVILY_API_KEY=<your_tavily_api_key>
      DEBUG=True
      ```

4. **Apply Migrations: (No need)**
    I uploaded the database for test `shopping_assistant.db`. So there is no need to apply migrations.
    If you wish to reset or modify the database, you can delete `shopping_assistant.db` and reapply migrations:
    ```bash
    python manage.py migrate
    ```

5. **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
    - Access the app at `http://127.0.0.1:8000/shopping_assistant/`.

---

## Usage

1. **User Registration and Login:**
   - Navigate to the homepage to create an account or log in.
   - In my tests, I use customer John Doe as the current user.
     - Username: johndoe
     - Password: password

2. **Shopping Assistant:**
   - Use the chat interface to interact with the assistant.
   - Query products, manage your cart, and get order-related details.

3. **Secure Operations:**
   - Sensitive actions like managing the cart require user confirmation.

---

## Testing

- Please refer to my test report for test cases.

---

## Folder Structure

```plaintext
shopping-assistant/
├── shopping_assistant/ # Main app logic
│   ├── assistants/     # Assistant logic
│   ├── utils/          # Tools and utilities
│   ├── tests/          # Tests in dev process 
│   ├── views.py        # Contains core functionalities
│   ├── models.py       # Database models
│   ├── urls.py         # URL routing
│   └── templates/      # HTML templates
├── shopping_project/
|   ├──settings.py
|   ├──urls.py
|   ├──asgi.py
|   ├──wsgi.py
├── static/             # CSS, JavaScript, images
├── manage.py           # Django entry point
├── requirements.txt    # Project dependencies
├── .env                # Environment variables
└── README.md           # Project documentation

```
## Contact

Please contact me if there is any problem.
