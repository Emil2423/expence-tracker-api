# Finance Tracker API Documentation

## Mobile Integration Guide

This document provides comprehensive API documentation for integrating mobile applications with the Finance Tracker backend.

---

## Table of Contents

1. [Base URL & Configuration](#base-url--configuration)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication-endpoints)
   - [Categories](#category-endpoints)
   - [Transactions](#transaction-endpoints)
   - [Budgets](#budget-endpoints)
5. [Data Models](#data-models)
6. [Best Practices](#best-practices-for-mobile-integration)

---

## Base URL & Configuration

### Base URL
```
Production: https://your-domain.com/api/
Development: http://localhost:8000/api/
```

### Headers

All authenticated requests must include:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
Accept: application/json
```

---

## Authentication

The API uses **JWT (JSON Web Tokens)** for authentication via `djangorestframework-simplejwt`.

### Token Types

| Token Type | Purpose | Expiration |
|------------|---------|------------|
| Access Token | Authenticate API requests | Short-lived (typically 5-60 minutes) |
| Refresh Token | Obtain new access tokens | Long-lived (typically 1-7 days) |

### Token Storage (Mobile)

- **iOS**: Store tokens in Keychain
- **Android**: Store tokens in EncryptedSharedPreferences
- **Never** store tokens in plain text or UserDefaults/SharedPreferences

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `204` | No Content (successful deletion) |
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (invalid/expired token) |
| `403` | Forbidden (permission denied) |
| `404` | Not Found |
| `500` | Server Error |

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message for this field"]
}
```

### Token Refresh Flow

When receiving a `401` response:

1. Attempt to refresh the token using `/api/auth/refresh/`
2. If refresh succeeds, retry the original request
3. If refresh fails, redirect user to login screen

---

## API Endpoints

---

## Authentication Endpoints

### 1. Register User

Create a new user account.

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

**Request Body:**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | Unique username (max 150 chars) |
| `email` | string | Yes | Unique email address |
| `password` | string | Yes | Password (validated for strength) |
| `password_confirm` | string | Yes | Must match password |
| `first_name` | string | No | User's first name |
| `last_name` | string | No | User's last name |

**Success Response:** `201 Created`

```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2026-02-02T10:30:00Z"
  }
}
```

**Error Response:** `400 Bad Request`

```json
{
  "email": ["A user with this email already exists."],
  "password_confirm": ["Passwords do not match."]
}
```

---

### 2. Login (Obtain Tokens)

Authenticate user and receive JWT tokens.

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

**Request Body:**

```json
{
  "username": "johndoe",
  "password": "SecurePassword123!"
}
```

**Success Response:** `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Error Response:** `401 Unauthorized`

```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 3. Refresh Token

Obtain a new access token using the refresh token.

**Endpoint:** `POST /api/auth/refresh/`

**Authentication:** Not required

**Request Body:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response:** `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Response:** `401 Unauthorized`

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

### 4. Get User Profile

Retrieve the authenticated user's profile.

**Endpoint:** `GET /api/auth/profile/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2026-02-02T10:30:00Z"
}
```

---

### 5. Update User Profile

Update the authenticated user's profile.

**Endpoint:** `PATCH /api/auth/profile/`

**Authentication:** Required

**Request Body:** (include only fields to update)

```json
{
  "first_name": "Jonathan",
  "last_name": "Doe"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | string | User's first name |
| `last_name` | string | User's last name |

**Success Response:** `200 OK`

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "Jonathan",
  "last_name": "Doe",
  "created_at": "2026-02-02T10:30:00Z"
}
```

---

### 6. Change Password

Change the authenticated user's password.

**Endpoint:** `POST /api/auth/change-password/`

**Authentication:** Required

**Request Body:**

```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!",
  "new_password_confirm": "NewSecurePassword456!"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `old_password` | string | Yes | Current password |
| `new_password` | string | Yes | New password (validated) |
| `new_password_confirm` | string | Yes | Must match new_password |

**Success Response:** `200 OK`

```json
{
  "message": "Password changed successfully."
}
```

**Error Response:** `400 Bad Request`

```json
{
  "old_password": ["Incorrect password."]
}
```

---

## Category Endpoints

Categories organize transactions into INCOME or EXPENSE types.

### 1. List Categories

Get all categories for the authenticated user.

**Endpoint:** `GET /api/categories/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "Salary",
    "type": "INCOME",
    "created_at": "2026-02-02T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Groceries",
    "type": "EXPENSE",
    "created_at": "2026-02-02T10:35:00Z"
  }
]
```

---

### 2. Create Category

Create a new category.

**Endpoint:** `POST /api/categories/`

**Authentication:** Required

**Request Body:**

```json
{
  "name": "Transportation",
  "type": "EXPENSE"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Category name (max 50 chars, unique per user) |
| `type` | string | Yes | Either `"INCOME"` or `"EXPENSE"` |

**Success Response:** `201 Created`

```json
{
  "id": 3,
  "name": "Transportation",
  "type": "EXPENSE",
  "created_at": "2026-02-02T11:00:00Z"
}
```

**Error Response:** `400 Bad Request`

```json
{
  "name": ["You already have a category with this name."]
}
```

---

### 3. Get Category

Retrieve a specific category.

**Endpoint:** `GET /api/categories/{id}/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
{
  "id": 2,
  "name": "Groceries",
  "type": "EXPENSE",
  "created_at": "2026-02-02T10:35:00Z"
}
```

---

### 4. Update Category

Update a category (full or partial update).

**Endpoint:** `PUT /api/categories/{id}/` or `PATCH /api/categories/{id}/`

**Authentication:** Required

**Request Body:**

```json
{
  "name": "Food & Groceries"
}
```

**Success Response:** `200 OK`

```json
{
  "id": 2,
  "name": "Food & Groceries",
  "type": "EXPENSE",
  "created_at": "2026-02-02T10:35:00Z"
}
```

---

### 5. Delete Category

Delete a category.

**Endpoint:** `DELETE /api/categories/{id}/`

**Authentication:** Required

**Success Response:** `204 No Content`

**Note:** Deleting a category will also delete all associated transactions and budgets (CASCADE).

---

## Transaction Endpoints

Transactions track income and expenses.

### 1. List Transactions

Get all transactions with optional filtering.

**Endpoint:** `GET /api/transactions/`

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start` | date | Filter transactions from this date (YYYY-MM-DD) |
| `end` | date | Filter transactions until this date (YYYY-MM-DD) |
| `category` | integer | Filter by category ID |
| `category_type` | string | Filter by category type (`INCOME` or `EXPENSE`) |
| `min_amount` | decimal | Minimum transaction amount |
| `max_amount` | decimal | Maximum transaction amount |

**Example Request:**

```
GET /api/transactions/?start=2026-01-01&end=2026-01-31&category_type=EXPENSE
```

**Success Response:** `200 OK`

```json
[
  {
    "id": 1,
    "category": 2,
    "category_name": "Groceries",
    "category_type": "EXPENSE",
    "amount": "150.00",
    "note": "Weekly grocery shopping",
    "date": "2026-01-15T14:30:00Z",
    "created_at": "2026-01-15T14:35:00Z"
  },
  {
    "id": 2,
    "category": 1,
    "category_name": "Salary",
    "category_type": "INCOME",
    "amount": "5000.00",
    "note": "January salary",
    "date": "2026-01-01T09:00:00Z",
    "created_at": "2026-01-01T09:05:00Z"
  }
]
```

---

### 2. Create Transaction

Create a new transaction.

**Endpoint:** `POST /api/transactions/`

**Authentication:** Required

**Request Body:**

```json
{
  "category": 2,
  "amount": "75.50",
  "note": "Dinner at restaurant",
  "date": "2026-02-02T19:30:00Z"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | integer | Yes | Category ID (must belong to user) |
| `amount` | decimal | Yes | Positive amount (min: 0.01) |
| `note` | string | No | Optional description |
| `date` | datetime | Yes | Transaction date (ISO 8601, cannot be in future) |

**Success Response:** `201 Created`

```json
{
  "id": 3,
  "category": 2,
  "category_name": "Groceries",
  "category_type": "EXPENSE",
  "amount": "75.50",
  "note": "Dinner at restaurant",
  "date": "2026-02-02T19:30:00Z",
  "created_at": "2026-02-02T19:35:00Z"
}
```

**Error Response:** `400 Bad Request`

```json
{
  "amount": ["Amount must be greater than zero."],
  "date": ["Transaction date cannot be in the future."]
}
```

---

### 3. Get Transaction

Retrieve a specific transaction.

**Endpoint:** `GET /api/transactions/{id}/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
{
  "id": 1,
  "category": 2,
  "category_name": "Groceries",
  "category_type": "EXPENSE",
  "amount": "150.00",
  "note": "Weekly grocery shopping",
  "date": "2026-01-15T14:30:00Z",
  "created_at": "2026-01-15T14:35:00Z"
}
```

---

### 4. Update Transaction

Update a transaction (full or partial update).

**Endpoint:** `PUT /api/transactions/{id}/` or `PATCH /api/transactions/{id}/`

**Authentication:** Required

**Request Body:**

```json
{
  "amount": "160.00",
  "note": "Weekly grocery shopping - updated"
}
```

**Success Response:** `200 OK`

```json
{
  "id": 1,
  "category": 2,
  "category_name": "Groceries",
  "category_type": "EXPENSE",
  "amount": "160.00",
  "note": "Weekly grocery shopping - updated",
  "date": "2026-01-15T14:30:00Z",
  "created_at": "2026-01-15T14:35:00Z"
}
```

---

### 5. Delete Transaction

Delete a transaction.

**Endpoint:** `DELETE /api/transactions/{id}/`

**Authentication:** Required

**Success Response:** `204 No Content`

---

### 6. Transaction Summary

Get aggregated transaction statistics.

**Endpoint:** `GET /api/transactions/summary/`

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start` | date | Start date for summary (YYYY-MM-DD) |
| `end` | date | End date for summary (YYYY-MM-DD) |

**Example Request:**

```
GET /api/transactions/summary/?start=2026-01-01&end=2026-01-31
```

**Success Response:** `200 OK`

```json
{
  "total_income": "5000.00",
  "total_expenses": "2500.00",
  "net_savings": "2500.00",
  "income_by_category": [
    {
      "category_id": 1,
      "category_name": "Salary",
      "total": "5000.00"
    }
  ],
  "expenses_by_category": [
    {
      "category_id": 2,
      "category_name": "Groceries",
      "total": "600.00"
    },
    {
      "category_id": 3,
      "category_name": "Transportation",
      "total": "200.00"
    }
  ]
}
```

---

### 7. Monthly Summary

Get month-by-month breakdown of income and expenses.

**Endpoint:** `GET /api/transactions/monthly-summary/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
[
  {
    "month": "2026-01",
    "total_income": "5000.00",
    "total_expenses": "2500.00",
    "net_savings": "2500.00"
  },
  {
    "month": "2026-02",
    "total_income": "5000.00",
    "total_expenses": "1800.00",
    "net_savings": "3200.00"
  }
]
```

---

## Budget Endpoints

Budgets set spending limits for specific categories.

### 1. List Budgets

Get all budgets for the authenticated user.

**Endpoint:** `GET /api/budgets/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
[
  {
    "id": 1,
    "category": 2,
    "category_name": "Groceries",
    "category_type": "EXPENSE",
    "amount": "500.00",
    "period": "MONTHLY",
    "start_date": "2026-02-01",
    "end_date": "2026-02-28",
    "spent": "150.00",
    "remaining": "350.00",
    "progress_percentage": 30.0,
    "created_at": "2026-02-01T10:00:00Z"
  }
]
```

---

### 2. Create Budget

Create a new budget.

**Endpoint:** `POST /api/budgets/`

**Authentication:** Required

**Request Body:**

```json
{
  "category": 3,
  "amount": "200.00",
  "period": "MONTHLY",
  "start_date": "2026-02-01",
  "end_date": "2026-02-28"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | integer | Yes | Category ID (must be EXPENSE type) |
| `amount` | decimal | Yes | Budget limit (min: 0.01) |
| `period` | string | Yes | `"WEEKLY"` or `"MONTHLY"` |
| `start_date` | date | Yes | Budget start date (YYYY-MM-DD) |
| `end_date` | date | Yes | Budget end date (YYYY-MM-DD) |

**Success Response:** `201 Created`

```json
{
  "id": 2,
  "category": 3,
  "category_name": "Transportation",
  "category_type": "EXPENSE",
  "amount": "200.00",
  "period": "MONTHLY",
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "spent": "0.00",
  "remaining": "200.00",
  "progress_percentage": 0.0,
  "created_at": "2026-02-02T12:00:00Z"
}
```

**Error Response:** `400 Bad Request`

```json
{
  "category": ["Budgets can only be set for expense categories."],
  "end_date": ["End date must be after start date."]
}
```

---

### 3. Get Budget

Retrieve a specific budget with spending progress.

**Endpoint:** `GET /api/budgets/{id}/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
{
  "id": 1,
  "category": 2,
  "category_name": "Groceries",
  "category_type": "EXPENSE",
  "amount": "500.00",
  "period": "MONTHLY",
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "spent": "150.00",
  "remaining": "350.00",
  "progress_percentage": 30.0,
  "created_at": "2026-02-01T10:00:00Z"
}
```

---

### 4. Update Budget

Update a budget (full or partial update).

**Endpoint:** `PUT /api/budgets/{id}/` or `PATCH /api/budgets/{id}/`

**Authentication:** Required

**Request Body:**

```json
{
  "amount": "600.00"
}
```

**Success Response:** `200 OK`

```json
{
  "id": 1,
  "category": 2,
  "category_name": "Groceries",
  "category_type": "EXPENSE",
  "amount": "600.00",
  "period": "MONTHLY",
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "spent": "150.00",
  "remaining": "450.00",
  "progress_percentage": 25.0,
  "created_at": "2026-02-01T10:00:00Z"
}
```

---

### 5. Delete Budget

Delete a budget.

**Endpoint:** `DELETE /api/budgets/{id}/`

**Authentication:** Required

**Success Response:** `204 No Content`

---

### 6. Budget Summary

Get overall budget summary with spending progress for active budgets.

**Endpoint:** `GET /api/budgets/summary/`

**Authentication:** Required

**Success Response:** `200 OK`

```json
{
  "total_budgeted": "700.00",
  "total_spent": "350.00",
  "total_remaining": "350.00",
  "total_income_this_month": "5000.00",
  "total_expenses_this_month": "1200.00",
  "over_budget_categories": [
    {
      "category_id": 3,
      "category_name": "Entertainment",
      "budgeted": "100.00",
      "spent": "150.00",
      "over_by": "50.00"
    }
  ],
  "budgets": [
    {
      "id": 1,
      "category": 2,
      "category_name": "Groceries",
      "amount": "500.00",
      "spent": "300.00",
      "remaining": "200.00",
      "progress_percentage": 60.0
    }
  ]
}
```

---

## Data Models

### User

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `username` | string | Unique username |
| `email` | string | Unique email address |
| `first_name` | string | First name |
| `last_name` | string | Last name |
| `created_at` | datetime | Account creation timestamp |

### Category

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `name` | string | Category name (max 50 chars) |
| `type` | string | `INCOME` or `EXPENSE` |
| `created_at` | datetime | Creation timestamp |

### Transaction

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `category` | integer | Category ID |
| `category_name` | string | Category name (read-only) |
| `category_type` | string | Category type (read-only) |
| `amount` | decimal | Transaction amount |
| `note` | string | Optional description |
| `date` | datetime | Transaction date |
| `created_at` | datetime | Creation timestamp |

### Budget

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier |
| `category` | integer | Category ID (EXPENSE only) |
| `category_name` | string | Category name (read-only) |
| `category_type` | string | Category type (read-only) |
| `amount` | decimal | Budget limit |
| `period` | string | `WEEKLY` or `MONTHLY` |
| `start_date` | date | Budget start date |
| `end_date` | date | Budget end date |
| `spent` | decimal | Amount spent (calculated, read-only) |
| `remaining` | decimal | Amount remaining (calculated, read-only) |
| `progress_percentage` | decimal | Percentage spent (calculated, read-only) |
| `created_at` | datetime | Creation timestamp |

---

## Best Practices for Mobile Integration

### 1. Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   App Start │────▶│ Check Token │────▶│   Valid?    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
            ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
            │  No Token     │          │ Token Valid   │          │ Token Expired │
            │  → Login      │          │ → Home Screen │          │ → Refresh     │
            └───────────────┘          └───────────────┘          └───────┬───────┘
                                                                          │
                                              ┌───────────────────────────┼───────────┐
                                              ▼                           ▼           │
                                      ┌───────────────┐           ┌───────────────┐   │
                                      │ Refresh OK    │           │ Refresh Fail  │   │
                                      │ → Home Screen │           │ → Login       │   │
                                      └───────────────┘           └───────────────┘   │
```

### 2. Offline Support

- Cache frequently accessed data (categories, recent transactions)
- Queue transactions created offline
- Sync when connection is restored
- Use timestamps for conflict resolution

### 3. Pagination (if implemented)

For large datasets, expect paginated responses:

```json
{
  "count": 150,
  "next": "http://api/transactions/?page=2",
  "previous": null,
  "results": [...]
}
```

### 4. Rate Limiting

Be mindful of potential rate limits:
- Implement exponential backoff
- Cache responses where appropriate
- Batch requests when possible

### 5. Date/Time Handling

- All dates are in ISO 8601 format
- Server times are in UTC
- Convert to user's local timezone on the client
- Send dates in UTC from the client

### 6. Decimal Handling

- All monetary amounts are strings to prevent floating-point errors
- Parse as Decimal/BigDecimal on mobile
- Never use float/double for money

### 7. Error Handling Example (Swift)

```swift
enum APIError: Error {
    case unauthorized
    case validationError([String: [String]])
    case serverError
    case networkError
}

func handleResponse<T: Decodable>(_ response: HTTPURLResponse, data: Data) throws -> T {
    switch response.statusCode {
    case 200...299:
        return try JSONDecoder().decode(T.self, from: data)
    case 401:
        throw APIError.unauthorized
    case 400:
        let errors = try JSONDecoder().decode([String: [String]].self, from: data)
        throw APIError.validationError(errors)
    default:
        throw APIError.serverError
    }
}
```

### 8. Error Handling Example (Kotlin)

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    object Unauthorized : ApiResult<Nothing>()
}

suspend fun <T> safeApiCall(apiCall: suspend () -> Response<T>): ApiResult<T> {
    return try {
        val response = apiCall()
        when {
            response.isSuccessful -> ApiResult.Success(response.body()!!)
            response.code() == 401 -> ApiResult.Unauthorized
            else -> ApiResult.Error(response.code(), response.message())
        }
    } catch (e: Exception) {
        ApiResult.Error(-1, e.message ?: "Unknown error")
    }
}
```

---

## API Quick Reference

| Action | Method | Endpoint |
|--------|--------|----------|
| Register | POST | `/api/auth/register/` |
| Login | POST | `/api/auth/login/` |
| Refresh Token | POST | `/api/auth/refresh/` |
| Get Profile | GET | `/api/auth/profile/` |
| Update Profile | PATCH | `/api/auth/profile/` |
| Change Password | POST | `/api/auth/change-password/` |
| List Categories | GET | `/api/categories/` |
| Create Category | POST | `/api/categories/` |
| Get Category | GET | `/api/categories/{id}/` |
| Update Category | PATCH | `/api/categories/{id}/` |
| Delete Category | DELETE | `/api/categories/{id}/` |
| List Transactions | GET | `/api/transactions/` |
| Create Transaction | POST | `/api/transactions/` |
| Get Transaction | GET | `/api/transactions/{id}/` |
| Update Transaction | PATCH | `/api/transactions/{id}/` |
| Delete Transaction | DELETE | `/api/transactions/{id}/` |
| Transaction Summary | GET | `/api/transactions/summary/` |
| Monthly Summary | GET | `/api/transactions/monthly-summary/` |
| List Budgets | GET | `/api/budgets/` |
| Create Budget | POST | `/api/budgets/` |
| Get Budget | GET | `/api/budgets/{id}/` |
| Update Budget | PATCH | `/api/budgets/{id}/` |
| Delete Budget | DELETE | `/api/budgets/{id}/` |
| Budget Summary | GET | `/api/budgets/summary/` |

---

## Support

For API issues or questions, contact the development team or open an issue in the repository.

**Version:** 1.0.0  
**Last Updated:** February 2, 2026
