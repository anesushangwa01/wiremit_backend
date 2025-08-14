# Wiremit Forex Aggregator API

A Django-based backend service for aggregating foreign exchange rates from multiple public APIs, calculating average rates, applying a markup for customer-facing rates, and storing rates persistently. Supports JWT authentication for secure access.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the API](#running-the-api)
- [Authentication](#authentication)
- [Rate Aggregation Logic](#rate-aggregation-logic)
- [API Endpoints](#api-endpoints)

## Features

- Fetches forex rates from multiple APIs: fastFOREX, Exchange Rates Data API, and APILayer.
- Calculates average rates and applies a configurable markup.
- Persists historical rates in a database.
- Auto-refreshes rates if data is older than 1 hour.
- JWT token-based authentication for secure API access.
- Provides historical, per-currency, and latest rates.

## Installation

Clone the repository:

```bash
git clone https://github.com/anesushangwa01/wiremit_backend.git
cd wiremit-backend
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Create a superuser (optional, for Django admin):

```bash
python manage.py createsuperuser
```

## Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True

DATABASE_URL=postgres://user:password@localhost:5432/yourdb or 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wiremit',
        'USER': 'wiremit',
        'HOST': 'localhost',
        'PASSWORD': '123',
    }
}



```

## Running the API

Start the development server:

```bash
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/.

## Authentication

This API uses JWT token authentication via Django REST Framework SimpleJWT.

Register a new user:

```http
POST /api/user/register/
Content-Type: application/json

{
  "username": "youruser",
  "email": "a123@gmail.com",
  "password": "yourpassword"
}
```

Obtain a token:

```http
POST /api/token/
Content-Type: application/json

{
  "username": "youruser",
  "password": "yourpassword"
}
```

Response:

```json
{
  "access": "ACCESS_TOKEN",
  "refresh": "REFRESH_TOKEN"
}
```





## Rate Aggregation Logic

The service fetches rates for predefined currency pairs from three APIs.

Rates from each API are collected, and the average rate is computed.

A markup (defined in .env) is added to the average rate to create a customer-facing rate.

Rates are saved in the AggregatedRate table with a timestamp.

When API endpoints are called, rates are auto-refreshed if older than 1 hour.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rates/` | GET | Returns the latest rates for all currency pairs. Optional query params: base, target. |
| `/api/rates/{currency}/` | GET | Returns latest rates where {currency} is the base or target. |
| `/api/rates/historical/` | GET | Returns all historical rates. |
| `/api/user/register` | POST | allow user to register for new account |
| `/api/users/login` | POST | allow user to login after register |
