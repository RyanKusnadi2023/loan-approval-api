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

#ORM model
"""
class Prediction(db.Model):
  __tablename__ = 'predictions'

  id = db.Column(db.Integer, primary_key=True)
  request_id = db.Column(db.String(36), nullable=False)
  input_data = db.Column(JSONB, nullable=False)
  prediction_result = db.Column(db.Integer, nullable=False)
  created_at = db.Column(db.DateTime, server_default=db.func.now())
"""

#Init DB - function buat init db, akan di call ryan di main
"""
db.create_all()
"""
#Save Prediction - function buat save prediction ke db
"""
db.session.add(new_prediction)
      db.session.commit()
"""


"""
Contoh hasil vibe coding

# crud.py
```python
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, nullable=False, index=True)
    input_data = Column(JSONB, nullable=False)
    prediction_result = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_prediction(db, request_id: str, input_data: dict, prediction_result: int):
    db_pred = Prediction(
        request_id=request_id,
        input_data=input_data,
        prediction_result=prediction_result
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred
```
"""