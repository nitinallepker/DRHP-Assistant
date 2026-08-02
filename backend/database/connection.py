import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Retrieve Database URL from environment, fallback to SQLite inside storage
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./storage/drhp_system.db")

# SQLite specific argument to support multi-threading in dev
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Provides a database session block for API endpoints, 
    safely yielding and releasing connections when complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
