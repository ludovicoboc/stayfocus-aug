from sqlalchemy import Column, String, Boolean, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    """Modelo de usuário que estende a autenticação do Supabase"""
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def is_authenticated(self):
        return self.is_active

class UserPreferences(Base, TimestampMixin):
    """Preferências do usuário"""
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    high_contrast = Column(Boolean, default=False)
    reduce_motion = Column(Boolean, default=False)
    large_text = Column(Boolean, default=False)
    theme = Column(String, default="system")


class DailyGoals(Base, TimestampMixin):
    """Metas diárias do usuário"""
    __tablename__ = "daily_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    goal_type = Column(String(20), nullable=False)  # sleep, tasks, hydration, breaks
    target_value = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint(
            "goal_type IN ('sleep', 'tasks', 'hydration', 'breaks')",
            name="check_goal_type"
        ),
    )
