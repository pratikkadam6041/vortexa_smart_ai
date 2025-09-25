from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base # Import Base from our database.py file

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # This creates a relationship so you can see all fields owned by a user
    fields = relationship("Field", back_populates="owner")

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String, index=True)
    location = Column(String)
    crop_type = Column(String)
    size_acres = Column(Float)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # This links a field back to its owner (a User)
    owner = relationship("User", back_populates="fields")