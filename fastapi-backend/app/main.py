from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

from app.database import Base, engine
from app.api.v1.api import api_router
from app.config import settings

# Cria as tabelas no banco de dados (em produção, usar migrações)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API para o aplicativo StayFocus - Gerenciamento de Produtividade",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da API
app.include_router(api_router, prefix="/api/v1")

# Rota de saúde
@app.get("/health")
async def health_check():
    """Verifica a saúde da API"""
    return {"status": "ok"}

# Rota raiz
@app.get("/")
async def root():
    """Rota raiz da API"""
    return {
        "message": "Bem-vindo à API do StayFocus",
        "docs": "/docs",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)