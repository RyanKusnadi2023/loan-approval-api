#main.py: App setup, endpoints, and dependency wiring
import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from services import preprocess_input, predict
from crud import SessionLocal, init_db, save_prediction
from schemas import LoanApplication, validate_payload

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()
"""

@app.get("/")
def health_check():
    return {"message": "Welcome to the Loan Approval Prediction API", "status": "Running"}

"""
@app.post("/predict", response_model=PredictionResponse)
def make_prediction(data: InputData, db: Session = Depends(get_db)):
    try:
        pred = predict(data.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    status = "Approved" if pred == 1 else "Rejected"
    try:
        save_prediction(db, str(uuid.uuid4()), data.dict(), pred)
    except:
        pass
    return PredictionResponse(prediction=pred, status=status)
"""
