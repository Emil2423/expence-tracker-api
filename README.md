# Personal Finance / Budget Tracker API

A Django REST Framework backend for tracking personal finances, managing budgets, and analyzing spending patterns.

## Features

- **User Authentication**: JWT-based authentication with registration, login, and password management
- **Category Management**: Create and manage income/expense categories
- **Transaction Tracking**: Log income and expenses with filtering and summaries
- **Budget Management**: Set spending limits by category with progress tracking
- **Monthly Summaries**: Chart-ready data for visualizing financial trends

## Tech Stack

- Django 5.x
- Django REST Framework
- Simple JWT for authentication
- SQLite (development) / PostgreSQL (production)

## Project Structure

```
finance_tracker/
├── finance_tracker/     # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/               # User authentication
├── transactions/        # Categories and transactions
├── budgets/             # Budget management
├── manage.py
└── requirements.txt
```

## Quick Start

### 1. Clone and Setup

```bash
cd expence-tracker-api

# Using venv (standard)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# OR Using Conda
conda create -n expense-tracker python=3.12 -y
conda activate expense-tracker

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env with your settings
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser (optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login and get tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET/PATCH | `/api/auth/profile/` | Get/Update user profile |
| POST | `/api/auth/change-password/` | Change password |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List categories |
| POST | `/api/categories/` | Create category |
| GET | `/api/categories/{id}/` | Get category |
| PUT/PATCH | `/api/categories/{id}/` | Update category |
| DELETE | `/api/categories/{id}/` | Delete category |

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions/` | List transactions |
| POST | `/api/transactions/` | Create transaction |
| GET | `/api/transactions/{id}/` | Get transaction |
| PUT/PATCH | `/api/transactions/{id}/` | Update transaction |
| DELETE | `/api/transactions/{id}/` | Delete transaction |
| GET | `/api/transactions/summary/` | Get summary |
| GET | `/api/transactions/monthly-summary/` | Get monthly data |

#### Transaction Filters

- `?start=YYYY-MM-DD` - Start date
- `?end=YYYY-MM-DD` - End date
- `?category=ID` - Filter by category
- `?category_type=INCOME|EXPENSE` - Filter by type
- `?min_amount=X` - Minimum amount
- `?max_amount=X` - Maximum amount

### Budgets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/budgets/` | List budgets |
| POST | `/api/budgets/` | Create budget |
| GET | `/api/budgets/{id}/` | Get budget |
| PUT/PATCH | `/api/budgets/{id}/` | Update budget |
| DELETE | `/api/budgets/{id}/` | Delete budget |
| GET | `/api/budgets/summary/` | Get budget summary |

## Example API Requests

### Register User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "StrongPass123!",
    "password_confirm": "StrongPass123!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "StrongPass123!"
  }'
```

### Create Transaction

```bash
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 1,
    "amount": "250.00",
    "note": "Grocery shopping",
    "date": "2026-02-02T14:30:00Z"
  }'
```

## Running Tests

```bash
python manage.py test
```

Or with pytest:

```bash
pytest
```

## Production Deployment

1. Set `DJANGO_DEBUG=False`
2. Generate a secure `DJANGO_SECRET_KEY`
3. Configure PostgreSQL database
4. Set proper `DJANGO_ALLOWED_HOSTS`
5. Configure CORS origins
6. Use gunicorn: `gunicorn finance_tracker.wsgi:application`

## License

MIT
