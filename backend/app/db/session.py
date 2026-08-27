from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine_url = settings.get_database_url()
if engine_url.startswith("sqlite"):
    engine = create_engine(engine_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(engine_url, pool_pre_ping=True)
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
