from app.crud import init_db, create_db, drop_db, save_prediction
from database import base

try:
    init_db()
    # drop_db()
    create_db()

    db = base.SessionLocal()
    user = save_prediction(
        db,
        person_age= 35.0,
        person_gender= "male",
        person_education="Bachelor",
        person_income=60000.0,
        person_emp_exp=10,
        person_home_ownership="RENT",
        loan_amnt=10000.0,
        loan_intent="PERSONAL",
        loan_int_rate=12.5,
        loan_percent_income=0.15,
        cb_person_cred_hist_length=4.0,
        credit_score=720,
        previous_loan_defaults_on_file= "No",
        prediction=1,
        confidence=0.2
    )
    
    print(f"result : {user}")
except Exception as e:
    print(f"err : ${e}")