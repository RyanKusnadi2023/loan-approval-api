#crud.py: SQLAlchemy setup, ORM model, and CRUD operations
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# SQLAlchemy setup
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_db():
    """
    Create database tables.
    """
    Base.metadata.create_all(bind=engine)
    return None


def save_prediction(db: Session, request_id: str, input_data: dict, prediction: int):
    """
    Save a prediction record to the database.
    """
    # TODO: implement actual save logic
    return {"id": 0, "request_id": request_id, "input_data": input_data, "prediction": prediction}



"""
db will be injected via main.
"""