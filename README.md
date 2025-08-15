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
# -----------------------
# API Keys
# -----------------------
CURRENCYFREAKS_KEY=xxxxxiiiiiiassssssss
FASTFOREX_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
APILAYER_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx!

# -----------------------
# Markup applied to average rate
# -----------------------
MARKUP_RATE=0.10  # e.g., 0.10 = 10% markup



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

user login

```http
POST /api/login/
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
Fetch all rates


```http
GET /api/rates/
Content-Type: application/json
 example:
{
 "count": 27,
    "results": [
        {
            "id": 150,
            "base_currency": "USD",
            "target_currency": "ZAR",
            "average_rate": "17.568888",
            "markup_rate": "19.325776",
            "fetched_at": "2025-08-15T11:28:18.651047+02:00"
        },
        {
            "id": 151,
            "base_currency": "ZAR",
            "target_currency": "GBP",
            "average_rate": "0.042030",
            "markup_rate": "0.046233",
            "fetched_at": "2025-08-15T11:28:18.651047+02:00"
        },
        {
            "id": 149,
            "base_currency": "USD",
            "target_currency": "GBP",
            "average_rate": "0.738424",
            "markup_rate": "0.812267",
            "fetched_at": "2025-08-15T11:28:18.645168+02:00"
        },
}
```

Fetch all by carrency
```http

GET  /api/rates/USD/
Content-Type: application/json

{
{
    "count": 18,
    "results": [
        {
            "id": 150,
            "base_currency": "USD",
            "target_currency": "ZAR",
            "average_rate": "17.568888",
            "markup_rate": "19.325776",
            "fetched_at": "2025-08-15T11:28:18.651047+02:00"
        },
        {
            "id": 149,
            "base_currency": "USD",
            "target_currency": "GBP",
            "average_rate": "0.738424",
            "markup_rate": "0.812267",
            "fetched_at": "2025-08-15T11:28:18.645168+02:00"
        },
        {
            "id": 147,
            "base_currency": "USD",
            "target_currency": "ZAR",
            "average_rate": "17.564828",
            "markup_rate": "19.321310",
            "fetched_at": "2025-08-15T10:35:37.841958+02:00"
        }.......
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
| `/api/register` | POST | allow user to register for new account |
| `/api/login` | POST | allow user to login after register |

## Optional ERD & Component structure & data flow image and a demo video :)


![WhatsApp Image 2025-08-15 at 12 27 52 PM](https://github.com/user-attachments/assets/9dda0aed-ca56-481e-bf99-0e806deea8a7)




![WhatsApp Image 2025-08-15 at 12 22 33 PM](https://github.com/user-attachments/assets/363a1d31-9655-44ca-82ed-bf81382b8705)








https://github.com/user-attachments/assets/cdf094f6-bcef-4f72-87c5-3aa0b614849a



