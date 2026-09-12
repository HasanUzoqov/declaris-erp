from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None
    company_id: Optional[int] = None

class UserLogin(BaseModel):
    phone: Optional[str] = None
    username: Optional[str] = None
    password: str

class UserResponse(UserBase):
    id: int
    full_name: Optional[str] = None
    role: str
    company_id: Optional[int] = None
    is_active: bool = True

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
