from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class BaseSchema(BaseModel):
    """Schema base com campos comuns"""
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Token(BaseModel):
    """Schema para o token de acesso"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema para os dados do token"""
    email: Optional[str] = None
    user_id: Optional[str] = None
