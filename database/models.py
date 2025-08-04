# app/database/models.py

from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
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

    users = relationship("User", back_populates="loans")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Float)
    gender = Column(String)
    education = Column(String)
    income = Column(Float)
    employ_expereience = Column(Integer)
    home_ownership = Column(String)

    loans = relationship("Loan", back_populates="users")
