from fastapi import APIRouter

from app.api.v1.endpoints import users, auth, tasks

api_router = APIRouter()

# Inclui os roteadores de cada módulo
api_router.include_router(auth.router, prefix="/auth", tags=["autenticação"])
api_router.include_router(users.router, prefix="/users", tags=["usuários"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tarefas"])
