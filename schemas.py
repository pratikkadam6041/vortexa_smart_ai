from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# --- Field Schemas (ADD THESE) ---
class FieldBase(BaseModel):
    field_name: str
    location: str
    size_acres: float
    crop_type: str | None = None

class FieldCreate(FieldBase):
    pass

class Field(FieldBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True