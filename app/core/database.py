from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import urllib.parse

# Build connection string
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={settings.DB_SERVER};"
    f"DATABASE={settings.DB_NAME};"
    f"UID={settings.DB_USER};"
    f"PWD={settings.DB_PASSWORD};"
    "TrustServerCertificate=yes;"
)

# Database connection URL
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=1800,  # Recycle connections after 30 minutes
    connect_args={
        "timeout": 30,  # Connection timeout in seconds
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 