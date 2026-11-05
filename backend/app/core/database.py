import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from a .env file if present
load_dotenv()

# Fetch the database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)


# Create a session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for database models to inherit from
Base = declarative_base()


def get_db():
    """FastAPI dependency for yielding database sessions safely."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

