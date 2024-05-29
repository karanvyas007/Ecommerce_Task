# Ecommerce Application

## Objective

This project is an e-commerce API built using Django Rest Framework to manage customers, orders, and products.

### User Registration and Authentication

- Users can create accounts and authenticate securely.
- User can updated/delete their details.
- User registration, login, and profile management.
- JWT-based authentication.
- Change/Update Password.

### Order Management

- Registered users can create, edit, and delete their own orders.
- Customer can have multiple orders and can add multiple products in cart.
- All users are allow to access Order APIs.
- Filter order results by customer name and product name.
 
### Technologies Used

- Python Version : 3.11.4
- Backend: Django (for Python-based backend development), Version : 3.15.1
- Database: postgresql

### Instruction To Run This Project

- Create a virtual environment to isolate project dependencies: python -m venv venv
- Activate the virtual environment: 
      - On Windows: venv\Scripts\activate
      - On macOS and Linux: source venv/bin/activate
- Install Dependencies: pip install -r requirements.txt
- Set Up Database: python manage.py migrate
- Start the Django development server: python manage.py runserver
- Open your web browser and navigate to http://127.0.0.1:8000/ to access the Blog Application.
- Access the Django admin panel at http://127.0.0.1:8000/admin/ using the superuser credentials created earlier.