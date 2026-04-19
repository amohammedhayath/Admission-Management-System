''' Required for database connection and session management. '''
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# ✅ Don't crash — fallback for safety
if not DATABASE_URL:
    print("⚠️ DATABASE_URL not found, using fallback SQLite")
    DATABASE_URL = "sqlite:///./fallback.db"

# ✅ PostgreSQL + SSL support
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"} if "postgresql" in DATABASE_URL else {}
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
