from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, TimestampMixin



class Task(Base, TimestampMixin):
    """Modelo de tarefa"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=2)  # 1: Baixa, 2: Média, 3: Alta
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    tags = Column(JSON, default=[])
    is_important = Column(Boolean, default=False)
    is_urgent = Column(Boolean, default=False)
    estimated_duration = Column(Integer, nullable=True)  # em minutos
    completed_at = Column(DateTime, nullable=True)

    # Relacionamentos
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task {self.title}>"

class Subtask(Base, TimestampMixin):
    """Subtarefas de uma tarefa principal"""
    __tablename__ = "subtasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    is_completed = Column(Boolean, default=False)

    # Relacionamentos
    task = relationship("Task", back_populates="subtasks")
    
    def __repr__(self):
        return f"<Subtask {self.title}>"

class TimeEntry(Base, TimestampMixin):
    """Registros de tempo gasto em uma tarefa"""
    __tablename__ = "time_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # em segundos
    notes = Column(Text, nullable=True)

    # Relacionamentos
    task = relationship("Task", back_populates="time_entries")
    
    def __repr__(self):
        return f"<TimeEntry {self.task_id} {self.start_time}>"
