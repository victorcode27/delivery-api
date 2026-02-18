"""
Database configuration using SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read DATABASE_URL directly from environment (no modification)
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLite-specific connection args (only applied for SQLite)
connect_args = {}
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create engine (works for both SQLite and PostgreSQL)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()
