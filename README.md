# Vue Flask Pharmacy Demo App

A demo full-stack web application for managing pharmacy products, users, carts, orders and comments.

This is a sanitized portfolio version of a university project.

## Features

- Public product catalog
- Product details page
- User registration and login
- JWT authentication
- Role-based access control
- Shopping cart
- Checkout system
- User profiles
- Product comments
- Admin user management
- Admin product management
- Admin comment management
- Responsive Bootstrap layout

## Tech Stack

- Vue 3
- Vite
- Vue Router
- Axios
- Bootstrap
- Python
- Flask
- MySQL / MariaDB
- Flask-JWT-Extended
- Flask-CORS

## Demo Accounts

Admin: admin / admin  
Seller: seller / seller  
Buyer: buyer / buyer

## Setup

### Database

Create a database named:

```sql
CREATE DATABASE pharmacy_demo;

Import the SQL dump:

database/pharmacy_demo.sql
Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
python src/main.py

The backend runs on:

http://127.0.0.1:5000
Frontend

Open another terminal:

cd frontend
npm install
copy .env.example .env
npm run dev

The frontend runs on:

http://127.0.0.1:5173
Note

The frontend API URL is configured in:

frontend/.env

Default value:

VITE_API_URL=http://127.0.0.1:5000