from src.config import settings

from sqlmodel import create_engine, Session

engine = create_engine(str(settings.DATABASE_URL), echo=True)

def get_session():
    with Session(engine) as session:
        yield session
