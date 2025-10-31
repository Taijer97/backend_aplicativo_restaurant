import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# URL de conexión MySQL (async)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost:3306/restaurant_db")

# Parámetros de pool configurables por .env
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # reciclar conexiones cada 30 min
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))    # espera para obtener conexión
DB_POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

# Crear motor async con configuración de pool
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_recycle=DB_POOL_RECYCLE,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_pre_ping=DB_POOL_PRE_PING,
)

# Sesión asíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base de modelos
Base = declarative_base()

# Dependencia para inyectar sesión
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session