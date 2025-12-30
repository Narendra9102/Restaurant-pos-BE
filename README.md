# Restaurant POS System – Backend (Django + DRF)

## Overview
This repository contains the backend of a Restaurant POS system built using **Django** and **Django REST Framework**.  

The system supports:
- Role-based authentication (Admin, Manager, Waiter, Cashier)
- Table management
- Menu management
- Order lifecycle
- Billing and payment handling
- Automatic table status updates using Django signals

This backend exposes REST APIs consumed by the frontend.

---

## Architecture
- **Framework:** Django, Django REST Framework
- **Auth:** Django Users + UserProfile for role management
- **Database:** MySQL (default) — can be changed in `settings.py`
- **Apps:**
  - `accounts` → User authentication, roles, RBAC
  - `restaurant` → Tables, Menu, Orders, Billing
- **Signals:** Automatic table status updates when orders are created or bills are paid

---

## User Roles & Permissions

| Role    | Capabilities |
|---------|--------------|
| Admin   | Create staff users (Manager, Waiter, Cashier) |
| Manager | CRUD tables and menu items |
| Waiter  | Create orders, update order status |
| Cashier | Generate bills, mark bills as paid |

**Note:** Admin = Django superuser in this workflow.

---

## Setup Instructions

### 1️. Clone the repository
```bash
git clone <backend-repo-url>
cd restaurant-pos-backend
````

### 2️. Create virtual environment

```bash
python -m venv venv
# Activate venv
# Linux/Mac: source venv/bin/activate
# Windows: venv\Scripts\activate
```

### 3️. Install dependencies

```bash
pip install -r requirements.txt
```

### 4️. Configure MySQL Database

Edit `backend/settings.py` and configure `DATABASES` section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'restaurant_pos_db',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

**Note:** Make sure the database exists or create it in MySQL:

```sql
CREATE DATABASE restaurant_pos_db;
```

---

### 5️. Create Django Superuser (Admin)

```bash
python manage.py createsuperuser
```

This superuser acts as **Admin** and can create:

* Only Admin can create staff accounts
* Manager
* Waiter
* Cashier accounts

---

### 6️. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 7️. Seed Sample Data

A simple seed file is provided to populate:
- Restaurant tables
- Menu items

Location:
- seed_data.py (project root)

Run:
python manage.py shell
>>> exec(open("seed_data.py").read())

Note:
User accounts are NOT seeded.
Admin must create Manager, Waiter, and Cashier users manually.
This follows real-world security best practices.

---

### 8️. Run the Server

```bash
python manage.py runserver
```

Backend runs at: `http://localhost:8000`

---

## Demo Credentials (Example)

| Role    | Username | Password   |
| ------- | -------- | ---------- |
| Admin   | admin    | admin123   |
| Manager | manager1 | manager123 |
| Waiter  | waiter1  | waiter123  |
| Cashier | cashier1 | cashier123 |

---

## Core Workflows

1. Manager creates tables & menu items
2. Waiter creates orders → Table automatically becomes `Occupied`
3. Waiter updates order status (Placed → In Kitchen → Served)
4. Cashier generates bill → marks it `Paid` → Table automatically becomes `Available`

---

## Database Migrations

All migrations are included under:

```
accounts/migrations/
restaurant/migrations/
```
