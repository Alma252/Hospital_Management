# 🏥 Hospital Management System - Backend API

A comprehensive **Hospital Management System** backend built with **Django REST Framework**, designed to manage patients, appointments, doctors, insurance, and invoicing.  
This project provides a robust RESTful API with **JWT Authentication**, Swagger/OpenAPI documentation, and support for **multi-insurance per patient** with real-time cost calculations.

---

## 🔧 Features

- ✅ Patient and Doctor Management  
- 🗓️ Appointment Scheduling with Availability Slots  
- 💳 Insurance System (Multiple insurances per patient with coverage %)  
- 📄 Invoice Generation (Cost calculation based on insurance coverage)  
- 🔐 JWT Authentication with `SimpleJWT`  
- 📚 Auto-generated Swagger API Docs  
- 🌍 CORS enabled for frontend consumption  
- 🛠️ Fully testable backend with no frontend required  


# API Endpoints
  For full documentation, visit /swagger/ or /redoc

# Setup Instructions
1. Clone the Repo
git clone https://github.com/your-username/hospital-management-backend.git
cd hospital-management-backend

2. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
pip install django djangorestframework
pip install djangorestframework-simplejwt
pip install drf-yasg
pip install django-cors-headers

4. Run Migrations
python manage.py makemigrations
python manage.py migrate

5. Create Superuser (for admin panel)
python manage.py createsuperuser

🚀 6. Run Server
python manage.py runserver

💡 Notes

    Admin Panel: http://127.0.0.1:8000/admin/

    Swagger Docs: http://127.0.0.1:8000/swagger/

    Redoc Docs: http://127.0.0.1:8000/redoc/


# Tech Stack 📌

    Python 3.10+

    Django 5.x

    Django REST Framework

    JWT (SimpleJWT)

    SQLite

    Swagger / Redoc


🤝 Contributing

Pull requests are welcome! Feel free to fork and contribute.
Please open an issue first for major changes.









