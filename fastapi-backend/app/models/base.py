from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func

# Cria a classe base para todos os modelos SQLAlchemy
Base = declarative_base()

class TimestampMixin:
    """Mixin que adiciona campos de data de criação e atualização"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

# Importa todos os modelos para garantir que sejam registrados com o SQLAlchemy
from app.models.user import User, UserPreferences, DailyGoals
from app.models.task import Task, Subtask, TimeEntry

# Exporta todos os modelos para facilitar as importações
__all__ = [
    'Base',
    'TimestampMixin',
    'User',
    'UserPreferences',
    'DailyGoals',
    'Task',
    'Subtask',
    'TimeEntry'
]
