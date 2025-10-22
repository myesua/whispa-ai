from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    privacy_mode: bool = True

class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    privacy_mode: bool