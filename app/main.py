"""Compatibility entrypoint.

Allows running either of these commands:
- From repo root: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- From backend dir: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
"""

from backend.app.main import app

__all__ = ["app"]
