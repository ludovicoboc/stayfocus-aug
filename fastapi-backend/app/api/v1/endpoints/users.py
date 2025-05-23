from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User, UserPreferences, DailyGoals
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, UserPreferences as UserPreferencesSchema
from app.auth.jwt import get_password_hash, get_current_active_user, get_current_user

router = APIRouter()

# Rotas de Usuários
@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário"""
    # Verifica se o email já está em uso
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Cria o usuário
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/me", response_model=UserSchema)
def read_user_me(current_user: User = Depends(get_current_active_user)):
    """Retorna os dados do usuário logado"""
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualiza os dados do usuário logado"""
    user_data = user_update.dict(exclude_unset=True)
    
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    
    for field, value in user_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user

# Rotas de Preferências do Usuário
@router.get("/me/preferences", response_model=UserPreferencesSchema)
def read_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retorna as preferências do usuário logado"""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Cria preferências padrão se não existirem
        preferences = UserPreferences(
            user_id=current_user.id,
            high_contrast=False,
            reduce_motion=False,
            large_text=False,
            theme="system"
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return preferences

@router.put("/me/preferences", response_model=UserPreferencesSchema)
def update_user_preferences(
    preferences_update: UserPreferencesSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Atualiza as preferências do usuário logado"""
    preferences = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        # Cria novas preferências se não existirem
        preferences_data = preferences_update.dict()
        preferences_data["user_id"] = current_user.id
        preferences = UserPreferences(**preferences_data)
    else:
        # Atualiza as preferências existentes
        update_data = preferences_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)
    
    db.add(preferences)
    db.commit()
    db.refresh(preferences)
    
    return preferences
