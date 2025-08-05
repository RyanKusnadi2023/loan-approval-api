# app/database/models.py

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database.base import Base

class Loan(Base):
    __tablename__ = 'loans'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    intent = Column(String)
    interest_rate = Column(Float)
    percent_income = Column(Float)
    cred_history_yearly = Column(Float)
    credit_score = Column(Integer)
    prev_loan_def = Column(String)
    loan_status = Column(String)
    confidence = Column(Float)
    create_date = Column(DateTime(timezone=True), server_default=func.now())
    create_by = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    update_by = Column(String)

    users = relationship("User", back_populates="loans")
    approval_loggers = relationship("ApprovalLogger", back_populates="loans")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Float)
    gender = Column(String)
    education = Column(String)
    income = Column(Float)
    employ_expereience = Column(Integer)
    home_ownership = Column(String)
    create_date = Column(DateTime(timezone=True), server_default=func.now())
    create_by = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    update_by = Column(String)

    loans = relationship("Loan", back_populates="users")
    
class ApprovalLogger(Base):
    __tablename__ = 'approval_loggers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_id = Column(Integer, ForeignKey('loans.id'))
    request_input = Column(JSONB)
    request_output = Column(JSONB)
    create_date = Column(DateTime(timezone=True), server_default=func.now())
    create_by = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    update_by = Column(String)
    
    loans = relationship("Loan", back_populates="approval_loggers")