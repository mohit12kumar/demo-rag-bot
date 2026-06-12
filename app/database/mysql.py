from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ==========================================
# Create Database If Not Exists
# ==========================================

TEMP_DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:"
    f"{settings.MYSQL_PASSWORD}@"
    f"{settings.MYSQL_HOST}:"
    f"{settings.MYSQL_PORT}"
)

temp_engine = create_engine(TEMP_DATABASE_URL)

with temp_engine.connect() as conn:
    conn.execute(
        text(
            f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE}"
        )
    )
    conn.commit()

# ==========================================
# Main Database Connection
# ==========================================

DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_USER}:"
    f"{settings.MYSQL_PASSWORD}@"
    f"{settings.MYSQL_HOST}:"
    f"{settings.MYSQL_PORT}/"
    f"{settings.MYSQL_DATABASE}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()