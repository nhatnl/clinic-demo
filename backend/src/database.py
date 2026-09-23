from sqlmodel import Session, create_engine

from src.config import settings

engine = create_engine(str(settings.DATABASE_URL), echo=True)


# We not using Async Session here due to no need for this phase of the project
def get_session():
    with Session(engine) as session:
        yield session
