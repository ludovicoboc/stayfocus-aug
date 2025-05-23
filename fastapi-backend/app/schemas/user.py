from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from .base import BaseSchema

# Schemas para Usuários
class UserBase(BaseSchema):
    """Schema base para usuário"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8, max_length=64)

class UserUpdate(BaseModel):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=64)
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    """Schema para usuário no banco de dados"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """Schema para retorno de usuário (sem senha)"""
    pass

# Schemas para Autenticação
class Token(BaseSchema):
    """Schema para resposta de token"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema para dados do token"""
    email: Optional[str] = None

class UserLogin(BaseModel):
    """Schema para login de usuário"""
    email: EmailStr
    password: str

# Schemas para Preferências do Usuário
class UserPreferencesBase(BaseModel):
    """Schema base para preferências do usuário"""
    high_contrast: bool = False
    reduce_motion: bool = False
    large_text: bool = False
    theme: str = "system"

class UserPreferencesCreate(UserPreferencesBase):
    """Schema para criação de preferências do usuário"""
    pass

class UserPreferencesUpdate(UserPreferencesBase):
    """Schema para atualização de preferências do usuário"""
    high_contrast: Optional[bool] = None
    reduce_motion: Optional[bool] = None
    large_text: Optional[bool] = None
    theme: Optional[str] = None

class UserPreferences(UserPreferencesBase):
    """Schema para retorno de preferências do usuário"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
