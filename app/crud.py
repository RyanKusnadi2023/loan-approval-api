import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from database.database_config import DatabaseConfig
from database import base
from database.models import User, Loan, ApprovalLogger
from database.validations import Validation
from .schemas import LoanApplication

load_dotenv()

def init_db():
    try:
        print("Initialize database ....")
        
        connection_string = DatabaseConfig(
            host=os.getenv("DB_HOST", '@localhost'),
            port=5432,
            database="loan_postgres",
            username="bdpit4",
            password="Bcabca1"
        ).connection_string
        
        # connection_string = DatabaseConfig(
        #     host=os.getenv("DB_HOST", '@localhost'),
        #     port=os.getenv("DB_PORT", 5432),
        #     database=os.getenv("DB_NAME", 'loan_postgres'),
        #     username=os.getenv("DB_USER", "bdpit4"),
        #     password=os.getenv("DB_PASSWORD", "Bcabca1")
        # ).conenction_string

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


# person_age: float,
# person_gender: str,
# person_education: str,
# person_income: float,
# person_emp_exp: int,
# person_home_ownership: str,
# loan_amnt: float,
# loan_intent: str,
# loan_int_rate: float,
# loan_percent_income: float,
# cb_person_cred_hist_length: float,
# credit_score: int,
# previous_loan_defaults_on_file: str,
# loan_status: int,
# confidence: str

def save_prediction(
    db: Session,
    input_data: LoanApplication,
    loan_status: str,
    confidence: str,
    request_id: str
):
    result = {
        "status": "success",
        "err_msg": []
    }
    
    # if str.lower(person_gender) not in ['female', 'male']:
    #     err_msg.append(f"Error: person_age -> {person_age} expected -> male/female")
    
    # if str.lower(person_education.replace(" ", "")) not in ['highschool', 'associate', 'bachelor', 'master', 'doctorate']:
    #     err_msg.append(f"Error: person_education -> {person_age} expected -> High School/Associate/Bachelor/Master/Doctorate")
    
    # if str.lower(person_home_ownership.replace(" ", "")) not in ['rent', 'own', 'mortgage', 'other']:
    #     err_msg.append(f"Error: person_home_ownership -> {person_age} expected -> RENT/OWN/MORTGAGE/OTHER")
        
    # if str.lower(loan_intent.replace(" ", "")) not in ['personal', 'education', 'medical', 'venture', 'homeimprovement']:
    #     err_msg.append(f"Error: person_home_ownership -> {person_age} expected -> PERSONAL/EDUCATION/MEDICAL/VENTURE/HOMEIMPROVEMENT")
    
    print(f">>> pgnder: {input_data}")
    try:
        if not Validation(input_data.person_gender).person_gender:
            result["err_msg"].append(f"Error: person_age -> {input_data.person_gender} expected -> male/female")
    except Exception as e:
        result["err_msg"].append(f"Error: failed validate person_age ({e}) ")
        
    try:
        if not Validation(input_data.person_education).person_education:
            result["err_msg"].append(f"Error: person_education -> {input_data.person_education} expected -> High School/Associate/Bachelor/Master/Doctorate")
    except Exception as e:
        result["err_msg"].append(f"Error: failed validate person_education ({e}) ")
        
    try:
        if not Validation(input_data.person_home_ownership).person_home_ownership:
            result["err_msg"].append(f"Error: person_home_ownership -> {input_data.person_home_ownership} expected -> RENT/OWN/MORTGAGE/OTHER")
    except Exception as e:
        result["err_msg"].append(f"Error: failed validate person_home_ownership ({e}) ")
        
    try:
        if not Validation(input_data.loan_intent).loan_intent:
            result["err_msg"].append(f"Error: loan_intent -> {input_data.loan_intent} expected -> PERSONAL/EDUCATION/MEDICAL/VENTURE/HOMEIMPROVEMENT")
            
    except Exception as e:
        result["err_msg"].append(f"Error: failed validate loan_intent ({e}) ")
        
    if len(result["err_msg"]) > 0:
        result["status"] = "failed"
        
        return result
    
    try:
        # user = User(
            # age=input_data.person_age,
            # gender=input_data.person_gender,
            # education=input_data.person_education,
            # income=input_data.person_income,
            # employ_expereience=input_data.person_emp_exp,
            # home_ownership=input_data.person_home_ownership,
            # create_by=request_id,
            # update_by=request_id,
        #     loans = [
        #         Loan(
        #             amount=input_data.loan_amnt,
        #             intent=input_data.loan_intent,
        #             interest_rate=input_data.loan_int_rate,
        #             percent_income=input_data.loan_percent_income,
        #             cred_history_yearly=input_data.cb_person_cred_hist_length,
        #             prev_loan_def=input_data.previous_loan_defaults_on_file,
        #             credit_score=input_data.credit_score,
        #             loan_status = loan_status,
        #             confidence=confidence,
        #             create_by=request_id,
        #             update_by=request_id,
        #         )
        #     ]
        # )
        
        loan = Loan(
            amount=input_data.loan_amnt,
            intent=input_data.loan_intent,
            interest_rate=input_data.loan_int_rate,
            percent_income=input_data.loan_percent_income,
            cred_history_yearly=input_data.cb_person_cred_hist_length,
            prev_loan_def=input_data.previous_loan_defaults_on_file,
            credit_score=input_data.credit_score,
            loan_status = loan_status,
            confidence=confidence,
            create_by=request_id,
            update_by=request_id,
            users= User(
                age=input_data.person_age,
                gender=input_data.person_gender,
                education=input_data.person_education,
                income=input_data.person_income,
                employ_expereience=input_data.person_emp_exp,
                home_ownership=input_data.person_home_ownership,
                create_by=request_id,
                update_by=request_id
            )
        )
        
        db.add(loan)
        db.commit()
        
        print(f">>>>>>>>> in db {loan.id}")
        
        insert_loan_predict_log(
            db,
            input_data,
            loan,
            result,
            request_id
        )
        
    except Exception as e:
        db.rollback()
        result["status"] = "failed"
        result["err_msg"].append(f"Error: failed to insert ({e})")
    
    return result

def insert_loan_predict_log(
    db: Session,
    input_data: LoanApplication,
    loan: Loan,
    response: object,
    request_id: str
):
    result = {
        "status": "success",
        "err_msg": ""
    }
    
    try:
        approval_loggers = ApprovalLogger(
            loan_id = int(loan.id),
            request_input = input_data.dict(),
            request_output = response,
            create_by=request_id,
            update_by=request_id,
        )
         
        db.add(approval_loggers)
        db.commit()
        
    except Exception as e:
        db.rollback()
        result["status"] = "failed"
        result["err_msg"] = str(e)
    
    return result
    