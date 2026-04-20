''' Required for database connection and session management. '''
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# print(f"DEBUG: DATABASE_URL = {repr(DATABASE_URL)}")
# ✅ Don't crash — fallback for safety
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please check your .env file.")


# ✅ PostgreSQL + SSL support
use_ssl = os.getenv("USE_SSL", "false").lower() == "true"

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"} if use_ssl else {}
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
