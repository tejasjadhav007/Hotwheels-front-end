import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def _build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_driver = os.getenv("DB_DRIVER", "sqlite").lower()
    if db_driver == "postgresql":
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "hotwheels")

        # Common config mistake: DB_HOST is set like "user@host".
        # Keep only the host segment so startup does not crash with name resolution error.
        if "@" in db_host:
            db_host = db_host.split("@")[-1]

        return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    default_sqlite_path = Path(__file__).resolve().parents[1] / "hotwheels.db"
    sqlite_path = os.getenv("SQLITE_PATH", str(default_sqlite_path))
    return f"sqlite:///{sqlite_path}"


DATABASE_URL = _build_database_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
