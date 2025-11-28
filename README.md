# Shopify API
My submission for project nexus is an  e-commerce based project, Shopify API. A comprehensive RESTful API built with **Django** and **Django REST Framework** for managing a complete e-commerce platform including products, categories, cart, orders, reviews, and user management.

## Quick start

**Clone repository & install dependencies**

```bash
git clone <repo-url>
cd shopify_api
python -m venv venv
source venv/bin/activate   # macOS / Linux
# On Windows: run venv\Scripts\activate
pip install -r requirements.txt
```

**Database setup and run**

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Open http://127.0.0.1:8000/
```

**Access API Documentation**
- Swagger UI: http://127.0.0.1:8000/swagger/
---

## Tech stack

* Python 3.10+
* Django 4.2+
* Django REST Framework (DRF)
* djangorestframework-simplejwt (JWT authentication)
* django-filter (Filtering support)
* drf-yasg (API documentation)
* PostgreSQL (Database)
* Pillow (Image handling)

---

## API endpoints (summary)

All API endpoints are prefixed with `/api/`.

```text
POST        /api/register/                          -> Register a new user (public)
POST        /api/token/                             -> Obtain JWT access and refresh tokens
POST        /api/token/refresh/                     -> Refresh access token

GET         /api/users/                             -> List all users (authenticated)
GET         /api/users/<int:pk>/                    -> Get specific user details (authenticated)
GET         /api/users/me/                          -> Get current user profile (authenticated)

GET/POST    /api/categories/                        -> List/create categories (authenticated for POST)
GET/PUT/DEL /api/categories/<int:pk>/               -> Retrieve/update/delete category (authenticated for PUT/DEL)

GET/POST    /api/products/                          -> List/create products (supports filtering, sorting, pagination)
GET/PUT/DEL /api/products/<int:pk>/                 -> Retrieve/update/delete product
GET         /api/products/featured/                 -> Get 10 newest products
GET         /api/products/<int:pk>/reviews/         -> Get all reviews for a product

GET/POST    /api/product-images/                    -> List/upload product images
GET/PUT/DEL /api/product-images/<int:pk>/           -> Retrieve/update/delete product image

GET/POST    /api/addresses/                         -> List/create user addresses (authenticated, user-specific)
GET/PUT/DEL /api/addresses/<int:pk>/                -> Retrieve/update/delete address (owner only)

GET         /api/cart/my_cart/                      -> Get current user's cart
POST        /api/cart/add_item/                     -> Add item to cart
PATCH       /api/cart/update_item/                  -> Update item quantity in cart
DELETE      /api/cart/remove_item/                  -> Remove item from cart
DELETE      /api/cart/clear/                        -> Clear entire cart
POST        /api/cart/checkout/                     -> Create order from cart and clear it

GET/POST    /api/orders/                            -> List/create orders (user-specific)
GET/PUT/DEL /api/orders/<int:pk>/                   -> Retrieve/update/delete order (owner only)
PATCH       /api/orders/<int:pk>/cancel/            -> Cancel order and restore stock (owner only)

GET/POST    /api/reviews/                           -> List/create reviews
GET/PUT/DEL /api/reviews/<int:pk>/                  -> Retrieve/update/delete review (owner only)
```

---

## Features

### **Product Management**
- Create, read, update, delete products
- Upload multiple images per product
- Filter by category, price range, stock availability
- Sort by price, date, name, stock
- Search by name or description
- Pagination support (10 items per page)

### **Shopping Cart**
- Add items to cart
- Update item quantities
- Remove items
- View cart totals
- One-click checkout

### **Order Management**
- Create orders from cart
- Automatic stock management
- Order status tracking (pending, processing, shipped, delivered, cancelled)
- Payment status tracking
- Cancel orders with stock restoration
- Separate shipping and billing addresses

### **Reviews & Ratings**
- Users can review products
- 1-5 star rating system
- One review per user per product
- Filter reviews by product or rating

### **Authentication & Authorization**
- JWT token-based authentication
- User registration with automatic token generation
- Users can only manage their own data (orders, addresses, cart, reviews)
- Admin privileges for certain operations

---

## Authentication

* **Register**: `POST /api/register/` — create a new user with automatic token generation
* **Obtain token**: `POST /api/token/` — returns `access` and `refresh` JWT tokens
* **Refresh token**: `POST /api/token/refresh/` — get new access token

For all protected endpoints include the `Authorization` header:

```
Authorization: Bearer <ACCESS_TOKEN>
```

---

## Product Filtering & Sorting

### **Filter by category**
```
GET /api/products/?category=1
```

### **Filter by price range**
```
GET /api/products/?price__gte=50&price__lte=200
# or
GET /api/products/?min_price=50&max_price=200
```

### **Filter by stock**
```
GET /api/products/?stock__gte=1  # In stock products
```

### **Filter by availability**
```
GET /api/products/?is_available=true
```

### **Search products**
```
GET /api/products/?search=laptop
```

### **Sort products**
```
GET /api/products/?ordering=price          # Ascending
GET /api/products/?ordering=-price         # Descending
GET /api/products/?ordering=-created_at    # Newest first
```

### **Pagination**
```
GET /api/products/?page=2&page_size=20
```

### **Combine filters**
```
GET /api/products/?category=1&price__lte=500&ordering=-price&page=1
```

---

## Examples (curl)

### 1) Register a user

```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","email":"john@example.com","password":"securepass123","first_name":"John","last_name":"Doe"}'
```

### 2) Obtain JWT tokens

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"securepass123"}'
```

**Response** (example)

```json
{
  "refresh": "<REFRESH_TOKEN>",
  "access": "<ACCESS_TOKEN>"
}
```

### 3) Create a product (authenticated)

```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"name":"iPhone 15 Pro","description":"Latest Apple smartphone","price":"999.99","stock":50,"category_id":1,"is_available":true}'
```

### 4) Add item to cart

```bash
curl -X POST http://127.0.0.1:8000/api/cart/add_item/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"product_id": 1, "quantity": 2}'
```

### 5) Checkout cart

```bash
curl -X POST http://127.0.0.1:8000/api/cart/checkout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"shipping_address_id": 1, "shipping_cost": 10.00}'
```

**Postman tip:**

* Use the *Headers* tab to add `Authorization: Bearer <ACCESS_TOKEN>` or choose Authorization ➜ Bearer Token.
* Also use the *Headers* tab to add `Content-Type: application/json`

---

## Examples (Postman)

### Registering a new account
```bash
POST http://127.0.0.1:8000/api/register/
Content-Type: application/json
```
**Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}
```
**Response:**
```json
{
    "user": {
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "access": "<ACCESS_TOKEN>",
    "refresh": "<REFRESH_TOKEN>"
}
```

---

### Logging in to get tokens
```bash
POST http://127.0.0.1:8000/api/token/
Content-Type: application/json
```
**Body:**
```json
{
    "username": "john_doe",
    "password": "securepass123"
}
```
**Response:**
```json
{
    "refresh": "<REFRESH_TOKEN>",
    "access": "<ACCESS_TOKEN>"
}
```

---

### Creating a category
```bash
POST http://127.0.0.1:8000/api/categories/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
}
```
**Response:**
```json
{
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "product_total": 0,
    "created_at": "2024-11-28T10:00:00Z",
    "updated_at": "2024-11-28T10:00:00Z"
}
```

---

### Listing all categories
```bash
GET http://127.0.0.1:8000/api/categories/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Electronics",
            "description": "Electronic devices",
            "product_total": 15,
            "created_at": "2024-11-28T10:00:00Z",
            "updated_at": "2024-11-28T10:00:00Z"
        },
        ...
    ]
}
```

---

### Creating a product
```bash
POST http://127.0.0.1:8000/api/products/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "name": "iPhone 15 Pro",
    "description": "Latest Apple smartphone with A17 Pro chip",
    "price": "999.99",
    "stock": 50,
    "category_id": 1,
    "is_available": true
}
```
**Response:**
```json
{
    "id": 1,
    "name": "iPhone 15 Pro",
    "description": "Latest Apple smartphone with A17 Pro chip",
    "price": "999.99",
    "stock": 50,
    "is_available": true,
    "is_in_stock": true,
    "category": {
        "id": 1,
        "name": "Electronics",
        "description": "Electronic devices",
        "product_total": 16,
        "created_at": "2024-11-28T10:00:00Z",
        "updated_at": "2024-11-28T10:00:00Z"
    },
    "images": [],
    "average_rating": 0,
    "review_count": 0,
    "created_at": "2024-11-28T12:00:00Z",
    "updated_at": "2024-11-28T12:00:00Z"
}
```

---

### Updating a product
```bash
PUT http://127.0.0.1:8000/api/products/1/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "name": "iPhone 15 Pro Max",
    "description": "Latest Apple smartphone with larger display",
    "price": "1199.99",
    "stock": 30,
    "category_id": 1,
    "is_available": true
}
```
**Response:**
```json
{
    "id": 1,
    "name": "iPhone 15 Pro Max",
    "description": "Latest Apple smartphone with larger display",
    "price": "1199.99",
    "stock": 30,
    "is_available": true,
    "is_in_stock": true,
    "category": {...},
    "images": [],
    "average_rating": 0,
    "review_count": 0,
    "created_at": "2024-11-28T12:00:00Z",
    "updated_at": "2024-11-28T12:30:00Z"
}
```

---

### Deleting a product
```bash
DELETE http://127.0.0.1:8000/api/products/1/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**No body required**

**Response:** `204 NO CONTENT`

---

### Listing products with filters
```bash
GET http://127.0.0.1:8000/api/products/?category=1&price__lte=1000&ordering=-price
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
    "count": 15,
    "next": "http://127.0.0.1:8000/api/products/?category=1&page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "iPhone 15 Pro",
            "description": "Latest Apple smartphone",
            "price": "999.99",
            "stock": 50,
            "is_available": true,
            "is_in_stock": true,
            "category": {...},
            "images": [...],
            "average_rating": 4.5,
            "review_count": 12,
            "created_at": "2024-11-28T12:00:00Z",
            "updated_at": "2024-11-28T12:00:00Z"
        },
        ...
    ]
}
```

---

### Creating an address
```bash
POST http://127.0.0.1:8000/api/addresses/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "address_type": "shipping",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "full_address": "123 Main Street, Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
}
```
**Response:**
```json
{
    "id": 1,
    "address_type": "shipping",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "full_address": "123 Main Street, Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA",
    "created_at": "2024-11-28T13:00:00Z",
    "updated_at": "2024-11-28T13:00:00Z"
}
```

---

### Adding item to cart
```bash
POST http://127.0.0.1:8000/api/cart/add_item/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "product_id": 1,
    "quantity": 2
}
```
**Response:**
```json
{
    "id": 1,
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "iPhone 15 Pro",
                "description": "Latest Apple smartphone",
                "price": "999.99",
                "stock": 48,
                "is_available": true,
                "is_in_stock": true,
                "category": {...},
                "images": [...],
                "average_rating": 4.5,
                "review_count": 12,
                "created_at": "2024-11-28T12:00:00Z",
                "updated_at": "2024-11-28T12:00:00Z"
            },
            "quantity": 2,
            "subtotal": "1999.98",
            "created_at": "2024-11-28T14:00:00Z",
            "updated_at": "2024-11-28T14:00:00Z"
        }
    ],
    "total_items": 2,
    "total_price": "1999.98",
    "created_at": "2024-11-28T14:00:00Z",
    "updated_at": "2024-11-28T14:00:00Z"
}
```

---

### Viewing cart
```bash
GET http://127.0.0.1:8000/api/cart/my_cart/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
    "id": 1,
    "items": [
        {
            "id": 1,
            "product": {...},
            "quantity": 2,
            "subtotal": "1999.98",
            "created_at": "2024-11-28T14:00:00Z",
            "updated_at": "2024-11-28T14:00:00Z"
        }
    ],
    "total_items": 2,
    "total_price": "1999.98",
    "created_at": "2024-11-28T14:00:00Z",
    "updated_at": "2024-11-28T14:00:00Z"
}
```

---

### Updating cart item quantity
```bash
PATCH http://127.0.0.1:8000/api/cart/update_item/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "product_id": 1,
    "quantity": 3
}
```
**Response:**
```json
{
    "id": 1,
    "items": [
        {
            "id": 1,
            "product": {...},
            "quantity": 3,
            "subtotal": "2999.97",
            "created_at": "2024-11-28T14:00:00Z",
            "updated_at": "2024-11-28T14:15:00Z"
        }
    ],
    "total_items": 3,
    "total_price": "2999.97",
    "created_at": "2024-11-28T14:00:00Z",
    "updated_at": "2024-11-28T14:15:00Z"
}
```

---

### Removing item from cart
```bash
DELETE http://127.0.0.1:8000/api/cart/remove_item/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "product_id": 1
}
```
**Response:**
```json
{
    "id": 1,
    "items": [],
    "total_items": 0,
    "total_price": "0.00",
    "created_at": "2024-11-28T14:00:00Z",
    "updated_at": "2024-11-28T14:20:00Z"
}
```

---

### Checkout (Create order from cart)
```bash
POST http://127.0.0.1:8000/api/cart/checkout/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "shipping_address_id": 1,
    "billing_address_id": 1,
    "shipping_cost": 10.00,
    "notes": "Please deliver after 5pm"
}
```
**Response:**
```json
{
    "id": 1,
    "order_number": "ORD-A1B2C3D4",
    "user_info": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "shipping_address": {
        "id": 1,
        "address_type": "shipping",
        "full_name": "John Doe",
        "phone_number": "+1234567890",
        "full_address": "123 Main Street, Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "created_at": "2024-11-28T13:00:00Z",
        "updated_at": "2024-11-28T13:00:00Z"
    },
    "billing_address": {...},
    "order_status": "pending",
    "payment_status": "unpaid",
    "subtotal": "2999.97",
    "shipping_cost": "10.00",
    "total": "3009.97",
    "notes": "Please deliver after 5pm",
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_name": "iPhone 15 Pro",
            "quantity": 3,
            "price": "999.99",
            "subtotal": "2999.97"
        }
    ],
    "item_count": 1,
    "created_at": "2024-11-28T15:00:00Z",
    "updated_at": "2024-11-28T15:00:00Z"
}
```

---

### Listing user orders
```bash
GET http://127.0.0.1:8000/api/orders/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "order_number": "ORD-A1B2C3D4",
            "user_info": {...},
            "shipping_address": {...},
            "billing_address": {...},
            "order_status": "pending",
            "payment_status": "unpaid",
            "subtotal": "2999.97",
            "shipping_cost": "10.00",
            "total": "3009.97",
            "notes": "Please deliver after 5pm",
            "items": [...],
            "item_count": 1,
            "created_at": "2024-11-28T15:00:00Z",
            "updated_at": "2024-11-28T15:00:00Z"
        },
        ...
    ]
}
```

---

### Canceling an order
```bash
PATCH http://127.0.0.1:8000/api/orders/1/cancel/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**No body required**

**Response:**
```json
{
    "id": 1,
    "order_number": "ORD-A1B2C3D4",
    "user_info": {...},
    "shipping_address": {...},
    "billing_address": {...},
    "order_status": "cancelled",
    "payment_status": "unpaid",
    "subtotal": "2999.97",
    "shipping_cost": "10.00",
    "total": "3009.97",
    "notes": "Please deliver after 5pm",
    "items": [...],
    "item_count": 1,
    "created_at": "2024-11-28T15:00:00Z",
    "updated_at": "2024-11-28T15:30:00Z"
}
```

---

### Creating a review
```bash
POST http://127.0.0.1:8000/api/reviews/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "product": 1,
    "rating": 5,
    "title": "Excellent product!",
    "comment": "Best smartphone I've ever used. Highly recommended!"
}
```
**Response:**
```json
{
    "id": 1,
    "product": 1,
    "product_name": "iPhone 15 Pro",
    "user_info": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "rating": 5,
    "title": "Excellent product!",
    "comment": "Best smartphone I've ever used. Highly recommended!",
    "created_at": "2024-11-28T16:00:00Z",
    "updated_at": "2024-11-28T16:00:00Z"
}
```

---

### Listing reviews for a product
```bash
GET http://127.0.0.1:8000/api/reviews/?product=1
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Response:**
```json
{
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "product": 1,
            "product_name": "iPhone 15 Pro",
            "user_info": {...},
            "rating": 5,
            "title": "Excellent product!",
            "comment": "Best smartphone I've ever used. Highly recommended!",
            "created_at": "2024-11-28T16:00:00Z",
            "updated_at": "2024-11-28T16:00:00Z"
        },
        ...
    ]
}
```

---

### Updating a review
```bash
PUT http://127.0.0.1:8000/api/reviews/1/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**Body:**
```json
{
    "product": 1,
    "rating": 4,
    "title": "Great product with minor issues",
    "comment": "Overall great, but battery life could be better."
}
```
**Response:**
```json
{
    "id": 1,
    "product": 1,
    "product_name": "iPhone 15 Pro",
    "user_info": {...},
    "rating": 4,
    "title": "Great product with minor issues",
    "comment": "Overall great, but battery life could be better.",
    "created_at": "2024-11-28T16:00:00Z",
    "updated_at": "2024-11-28T16:30:00Z"
}
```

---

### Deleting a review
```bash
DELETE http://127.0.0.1:8000/api/reviews/1/
Content-Type: application/json
Authorization: Bearer <ACCESS_TOKEN>
```
**No body required**

**Response:** `204 NO CONTENT`

---

## Error Responses

### 400 Bad Request
```json
{
    "error": "Insufficient stock for iPhone 15 Pro, Available: 5"
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "error": "Product not found."
}
```

---

## Database Schema

### Models Overview

**User** → Has many: Addresses, Orders, Reviews, one Cart

**Category** → Has many: Products

**Product** → Belongs to: Category | Has many: ProductImages, OrderItems, CartItems, Reviews

**ProductImage** → Belongs to: Product

**Address** → Belongs to: User

**Order** → Belongs to: User, Address (shipping & billing) | Has many: OrderItems

**OrderItem** → Belongs to: Order, Product

**Cart** → Belongs to: User (One-to-One) | Has many: CartItems

**CartItem** → Belongs to: Cart, Product

**Review** → Belongs to: User, Product

---

## Notes

* Access tokens expire after 15 minutes
* Refresh tokens expire after 7 days
* Stock is automatically reduced when orders are created
* Stock is automatically restored when orders are cancelled
* Users can only cancel orders with status 'pending' or 'processing'
* Each user can only write one review per product
* Cart items are automatically cleared after successful checkout
* All prices are in USD with 2 decimal places
* Product images are stored in `media/products/%Y/%m/%d/`

---
