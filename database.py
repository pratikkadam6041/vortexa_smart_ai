from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL. This will create a file named vortexa.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./vortexa.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of SessionLocal will be a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This Base class will be used to create our database models
Base = declarative_base()
