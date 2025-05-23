from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from uuid import UUID
from .base import BaseSchema

# Schemas para Tarefas
class TaskBase(BaseSchema):
    """Schema base para tarefas"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = Field(1, ge=1, le=3)  # 1-3: Baixa, Média, Alta
    status: str = "pending"  # pending, in_progress, completed, cancelled
    tags: List[str] = []
    is_important: bool = False
    is_urgent: bool = False
    estimated_duration: Optional[int] = Field(None, gt=0)  # em minutos

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v

class TaskCreate(TaskBase):
    """Schema para criação de tarefa"""
    pass

class TaskUpdate(BaseModel):
    """Schema para atualização de tarefa"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    is_important: Optional[bool] = None
    is_urgent: Optional[bool] = None
    estimated_duration: Optional[int] = Field(None, gt=0)
    completed_at: Optional[datetime] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of {valid_statuses}")
        return v

class TaskInDBBase(TaskBase):
    """Schema base para tarefa no banco de dados"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    """Schema para retorno de tarefa"""
    pass

# Schemas para Subtarefas
class SubtaskBase(BaseSchema):
    """Schema base para subtarefas"""
    title: str = Field(..., max_length=200)
    is_completed: bool = False

class SubtaskCreate(SubtaskBase):
    """Schema para criação de subtarefa"""
    pass

class SubtaskUpdate(BaseModel):
    """Schema para atualização de subtarefa"""
    title: Optional[str] = Field(None, max_length=200)
    is_completed: Optional[bool] = None

class SubtaskInDBBase(SubtaskBase):
    """Schema base para subtarefa no banco de dados"""
    id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Subtask(SubtaskInDBBase):
    """Schema para retorno de subtarefa"""
    pass

# Schemas para Registros de Tempo
class TimeEntryBase(BaseSchema):
    """Schema base para registros de tempo"""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0)  # em segundos
    notes: Optional[str] = None

class TimeEntryCreate(TimeEntryBase):
    """Schema para criação de registro de tempo"""
    pass

class TimeEntryUpdate(BaseModel):
    """Schema para atualização de registro de tempo"""
    end_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class TimeEntryInDBBase(TimeEntryBase):
    """Schema base para registro de tempo no banco de dados"""
    id: UUID
    task_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TimeEntry(TimeEntryInDBBase):
    """Schema para retorno de registro de tempo"""
    pass

# Schemas para respostas com relacionamentos
class TaskWithSubtasks(Task):
    """Schema de tarefa com subtarefas"""
    subtasks: List[Subtask] = []

class TaskWithTimeEntries(Task):
    """Schema de tarefa com registros de tempo"""
    time_entries: List[TimeEntry] = []

class TaskFull(Task):
    """Schema completo de tarefa com todos os relacionamentos"""
    subtasks: List[Subtask] = []
    time_entries: List[TimeEntry] = []
