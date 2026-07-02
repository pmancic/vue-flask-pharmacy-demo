# Vue Flask Pharmacy Demo App

This is a sanitized portfolio version of a university full-stack web application project.

The app is a demo pharmacy shop with a Vue 3 frontend, a Flask REST API backend, and a MySQL/MariaDB database. It includes authentication, role-based access, product management, a shopping cart, checkout, comments, user profiles, and admin pages.

## Tech Stack

### Frontend

- Vue 3
- Vite
- Vue Router
- Axios
- Bootstrap 5
- Vue Toast Notification

### Backend

- Python
- Flask
- Flask-CORS
- Flask-JWT-Extended
- MySQL Connector/Python
- python-dotenv
- Werkzeug password hashing

### Database

- MySQL / MariaDB
- SQL dump included in `database/pharmacy_demo.sql`

## Features

- User registration and login
- JWT authentication
- Role-based access control
  - `administrator`
  - `prodavac`
  - `kupac`
- Product listing and product details
- Add, edit, and delete products
- Shopping cart and checkout
- User profiles and balance updates
- Product comments
- Admin user management
- Admin product management
- Admin comment management

## Project Structure

```txt
.
├── backend/
│   ├── src/
│   │   └── main.py
│   ├── .env.example
│   ├── requirements.txt
│   ├── start_console.bat
│   └── start_flask_server.bat
├── frontend/
│   ├── src/
│   │   ├── api.js
│   │   ├── components/
│   │   ├── router/
│   │   └── views/
│   ├── .env.example
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── database/
│   └── pharmacy_demo.sql
└── README.md
```

## Requirements

- Node.js `20.19+` or `22.12+`
- Python `3.10+`
- MySQL or MariaDB
- npm

## Database Setup

Create a database named:

```sql
CREATE DATABASE pharmacy_demo;
```

Then import the SQL file:

```txt
database/pharmacy_demo.sql
```

Using phpMyAdmin:

1. Open phpMyAdmin.
2. Create a database named `pharmacy_demo`.
3. Select the database.
4. Go to **Import**.
5. Import `database/pharmacy_demo.sql`.

Or using terminal:

```bash
mysql -u root -p pharmacy_demo < database/pharmacy_demo.sql
```

## Backend Setup

Open a terminal in the project root, then run:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

Install backend dependencies:

```bash
python -m pip install -r requirements.txt
```

Create your local environment file:

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Default local database values are:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=pharmacy_demo
```

Run the backend:

```bash
python src/main.py
```

The backend should start on:

```txt
http://127.0.0.1:5000
```

## Frontend Setup

Open another terminal in the project root, then run:

```bash
cd frontend
npm install
npm run dev
```

The frontend should start on:

```txt
http://127.0.0.1:5173
```

The frontend API base URL is configured in `frontend/.env.example`:

```env
VITE_API_URL=http://127.0.0.1:5000
```

## Demo Accounts

The included SQL dump contains these demo users:

```txt
admin / admin
seller / seller
buyer / buyer
```

Roles:

```txt
admin  -> administrator
seller -> prodavac
buyer  -> kupac
```

## Build Frontend for Production

```bash
cd frontend
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

## Main Frontend Routes

```txt
/products              Product list
/products/:id          Product details
/products/add          Add product
/products/edit/:id     Edit product
/register              Register
/login                 Login
/profile/:username     User profile
/cart                  Shopping cart
/admin/users           Admin users
/admin/users/add       Add user as admin
/admin/products        Admin products
/admin/comments        Admin comments
```

## Main Backend API Routes

```txt
POST   /register
POST   /login
GET    /profile/<username>
PUT    /profile/update

GET    /products
POST   /products/add
PUT    /products/update/<product_id>
DELETE /products/delete/<product_id>

GET    /cart
POST   /cart/add/<product_id>
PUT    /cart/update/<product_id>
DELETE /cart/delete/<product_id>
POST   /checkout

GET    /products/<product_id>/comments
POST   /products/<product_id>/comment
PUT    /products/<product_id>/comment/update/<comment_id>
DELETE /products/<product_id>/comment/delete/<comment_id>

GET    /admin/users
POST   /admin/users/add
PUT    /admin/users/update/<user_id>
DELETE /admin/users/delete/<user_id>

GET    /admin/products
PUT    /admin/products
DELETE /admin/products/<product_id>

GET    /admin/comments
PUT    /admin/comments/<comment_id>
DELETE /admin/comments/<comment_id>
```

## GitHub Upload Notes

Do not upload generated dependencies or private files. This public version does not include `.git`, `.env`, old database history, cart/order demo records, or private author/student data.

Before committing, make sure these are not staged:

```txt
frontend/node_modules/
frontend/dist/
backend/.venv/
.env
frontend/.env
backend/.env
*.zip
```

## Useful Git Commands

```bash
git init
git branch -M main
git add .
git status
git commit -m "Initial public portfolio version"
git remote add origin https://github.com/YOUR_USERNAME/flask-vue-pharmacy-demo.git
git push -u origin main
```
