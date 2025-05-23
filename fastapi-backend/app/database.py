from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

# Importa os modelos para garantir que sejam registrados com o SQLAlchemy
from app.models.base import Base

# Cria a engine do SQLAlchemy
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Configurações extras para SQLite
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Cria a engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True  # Verifica a conexão antes de usá-la
)

# Cria uma fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Fornece uma sessão do banco de dados para cada requisição.
    Fecha a sessão quando a requisição é finalizada.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
