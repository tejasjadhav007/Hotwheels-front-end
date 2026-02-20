# Hotwheels Python Backend

FastAPI backend for the Hotwheels frontend with env-driven database configuration.

## Quick start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment

Copy from repository root:

```bash
cp .env.example .env
```

Defaults use SQLite. To use PostgreSQL, set `DB_DRIVER=postgresql` and update credentials.

## Demo users

- `admin@hotwheels.com` / `admin123`
- `customer@example.com` / `customer123`

## API routes

- `GET /health`
- `POST /api/auth/login`
- `GET /api/categories`
- `GET /api/products`
- `GET /api/products/{product_id}`
- `GET /api/cart/{user_id}`
- `POST /api/cart/{user_id}/items`
- `PATCH /api/cart/{user_id}/items/{product_id}`
- `DELETE /api/cart/{user_id}/items/{product_id}`
- `GET /api/orders/{user_id}`
- `POST /api/orders`
