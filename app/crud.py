import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from database.database_config import DatabaseConfig
from database import base
from database.models import User, Loan

load_dotenv()

def init_db():
    try:
        print("Initialize database ....")
        connection_string = DatabaseConfig(
            host='@localhost',
            port=5432,
            database='loan_postgres',
            username="bdpit4",
            password="Bcabca1"
        ).conenction_string

        print(f">>>> connection string: {connection_string}")
        
        base.engine = create_engine(connection_string, echo=True)

        base.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=base.engine
        )

        with base.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("Database connection successful!")

        print("Database initialization completed!")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
    
def create_db():
    try:
        if base.engine is None:
            init_db()

        print("Creating database ...")
        base.Base.metadata.create_all(base.engine)
        print("Successfully created database ...")
    except Exception as e:
        print(f"Failed to create database: {e}")
        
def drop_db():
    try:
        base.Base.metadata.drop_all(base.engine)
    except Exception as e:
         print(f"Failed to drop database: {e}")


def save_prediction(
    db: Session,
    person_age: float,
    person_gender: str,
    person_education: str,
    person_income: float,
    person_emp_exp: int,
    person_home_ownership: str,
    loan_amnt: float,
    loan_intent: str,
    loan_int_rate: float,
    loan_percent_income: float,
    cb_person_cred_hist_length: float,
    credit_score: int,
    previous_loan_defaults_on_file: str,
    prediction: int,
    confidence: float
) -> str:
    err_msg = []
    
    if str.lower(person_gender) not in ['female', 'male']:
        err_msg.append(f"Error: person_age -> {person_age} expected -> male/female")
    
    if str.lower(person_education.replace(" ", "")) not in ['highschool', 'associate', 'bachelor', 'master', 'doctorate']:
        err_msg.append(f"Error: person_education -> {person_age} expected -> High School/Associate/Bachelor/Master/Doctorate")
        
    if str.lower(person_home_ownership.replace(" ", "")) not in ['rent', 'own', 'mortgage', 'other']:
        err_msg.append(f"Error: person_home_ownership -> {person_age} expected -> RENT/OWN/MORTGAGE/OTHER")
        
    if str.lower(loan_intent.replace(" ", "")) not in ['personal', 'education', 'medical', 'venture', 'homeimprovement']:
        err_msg.append(f"Error: person_home_ownership -> {person_age} expected -> PERSONAL/EDUCATION/MEDICAL/VENTURE/HOMEIMPROVEMENT")
        
    if len(err_msg) > 0:
        return "\n".join(err_msg)
    
    loan_status_string = "approve" if prediction == 1  else "" 
    
    
    user = User(
        age=person_age,
        gender=person_gender,
        education=person_education,
        income=person_income,
        employ_expereience=person_emp_exp,
        home_ownership=person_home_ownership,
        loans = [
            Loan(
                amount=loan_amnt,
                intent=loan_intent,
                interest_rate=loan_int_rate,
                percent_income=loan_percent_income,
                cred_history_yearly=cb_person_cred_hist_length,
                prev_loan_def=previous_loan_defaults_on_file,
                credit_score=credit_score,
                loan_status = loan_status_string,
                confidence=confidence
            )
        ]
    )
    
    db.add(user)
    db.commit()
    
    return f"success create user : {user}"