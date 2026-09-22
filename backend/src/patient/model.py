from src.model import BaseModel
from sqlmodel import Field

class Patient(BaseModel, table=True):
    __tablename__ = "patients"
    
    name: str = Field(nullable=False, min_length=3, max_length=50)
    age: int = Field(nullable=False, ge=0, le=150)

