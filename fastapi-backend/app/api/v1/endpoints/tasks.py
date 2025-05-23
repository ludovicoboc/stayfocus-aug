from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.task import Task, Subtask, TimeEntry
from app.schemas.task import (
    TaskCreate, TaskUpdate, Task, TaskWithSubtasks, TaskWithTimeEntries, TaskFull,
    SubtaskCreate, SubtaskUpdate, Subtask,
    TimeEntryCreate, TimeEntryUpdate, TimeEntry
)
from app.auth.jwt import get_current_active_user
from app.models.user import User

router = APIRouter()

# --- Rotas de Tarefas ---

@router.get("/", response_model=List[Task])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[int] = None,
    is_important: Optional[bool] = None,
    is_urgent: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista todas as tarefas do usuário com filtros opcionais"""
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    # Aplica filtros
    if status:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if is_important is not None:
        query = query.filter(Task.is_important == is_important)
    if is_urgent is not None:
        query = query.filter(Task.is_urgent == is_urgent)
    if search:
        search = f"%{search}%"
        query = query.filter(
            or_(
                Task.title.ilike(search),
                Task.description.ilike(search)
            )
        )
    
    # Ordena por prioridade (alta para baixa) e data de vencimento (mais próxima primeiro)
    tasks = query.order_by(
        Task.priority.desc(),
        Task.due_date.asc(),
        Task.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return tasks

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cria uma nova tarefa"""
    db_task = Task(**task.model_dump(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/{task_id}", response_model=TaskFull)
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém uma tarefa específica com todos os seus relacionamentos"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza uma tarefa existente"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Atualiza os campos fornecidos
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    # Se a tarefa foi marcada como concluída, define a data de conclusão
    if update_data.get('status') == 'completed' and not db_task.completed_at:
        db_task.completed_at = datetime.utcnow()
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove uma tarefa"""
    db_task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    db.delete(db_task)
    db.commit()
    
    return None

# --- Rotas de Subtarefas ---

@router.get("/{task_id}/subtasks", response_model=List[Subtask])
async def list_subtasks(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista todas as subtarefas de uma tarefa"""
    # Verifica se a tarefa pertence ao usuário
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    return task.subtasks

@router.post(
    "/{task_id}/subtasks",
    response_model=Subtask,
    status_code=status.HTTP_201_CREATED
)
def create_subtask(
    task_id: UUID,
    subtask: SubtaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Adiciona uma subtarefa a uma tarefa existente"""
    # Verifica se a tarefa pertence ao usuário
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    db_subtask = Subtask(**subtask.model_dump(), task_id=task_id)
    db.add(db_subtask)
    db.commit()
    db.refresh(db_subtask)
    
    return db_subtask

# --- Rotas de Registros de Tempo ---

@router.post(
    "/{task_id}/time-entries",
    response_model=TimeEntry,
    status_code=status.HTTP_201_CREATED
)
def create_time_entry(
    task_id: UUID,
    time_entry: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Registra tempo gasto em uma tarefa"""
    # Verifica se a tarefa pertence ao usuário
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    # Se não foi fornecida a duração, calcula com base no start_time e end_time
    entry_data = time_entry.model_dump()
    if entry_data['end_time'] and not entry_data['duration']:
        duration = (entry_data['end_time'] - entry_data['start_time']).total_seconds()
        entry_data['duration'] = int(duration)
    
    db_time_entry = TimeEntry(
        **entry_data,
        task_id=task_id,
        user_id=current_user.id
    )
    
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    
    return db_time_entry

@router.get("/time-entries/summary")
def get_time_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    group_by: str = "day",  # day, week, month
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém um resumo do tempo gasto em tarefas"""
    from sqlalchemy import func, extract, case, and_
    
    # Filtra por datas, se fornecidas
    filters = [TimeEntry.user_id == current_user.id]
    if start_date:
        filters.append(TimeEntry.start_time >= start_date)
    if end_date:
        filters.append(TimeEntry.start_time <= end_date)
    
    # Agrupa por período
    if group_by == "day":
        date_trunc = func.date_trunc('day', TimeEntry.start_time)
    elif group_by == "week":
        date_trunc = func.date_trunc('week', TimeEntry.start_time)
    elif group_by == "month":
        date_trunc = func.date_trunc('month', TimeEntry.start_time)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="group_by deve ser 'day', 'week' ou 'month'"
        )
    
    # Query para somar o tempo gasto por período
    summary = db.query(
        date_trunc.label('period'),
        func.sum(TimeEntry.duration).label('total_duration'),
        func.count(TimeEntry.id).label('entry_count')
    ).filter(*filters).group_by('period').order_by('period').all()
    
    return [{
        'period': row.period,
        'total_duration': row.total_duration or 0,
        'entry_count': row.entry_count
    } for row in summary]
