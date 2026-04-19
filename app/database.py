''' Required for database connection and session management. '''
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 🔥 Ensure DB URL exists
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# 🔥 PostgreSQL engine (NO SQLite args)
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
