from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

connect_args = {}
if "postgres.database.azure.com" in settings.DB_HOST:
    connect_args = {"sslmode": "require"}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
