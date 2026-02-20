# Hotwheels Frontend + Backend

This repository includes:

- `src/` React + Vite frontend
- `backend/` FastAPI backend with SQLite/PostgreSQL support via `.env`

## Local development

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API docs: `http://localhost:8000/docs`

If you run backend from repository root, use:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production deployment (Linux)

For a complete server setup (requirements, systemd, nginx reverse proxy, SSL, verification, and update flow), see:

- [`DEPLOYMENT.md`](./DEPLOYMENT.md)
