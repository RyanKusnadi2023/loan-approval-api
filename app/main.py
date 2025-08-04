#main.py: App setup, endpoints, and dependency wiring
import os
import uuid 
import logging 
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import ValidationError

from services import load_resources, preprocess_input, predict
#from crud import SessionLocal, init_db, save_prediction
from schemas import LoanApplication, validate_payload

#Load environment variables and init components
load_dotenv()

#Logging setup
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, 'request_id', 'N/A')
        return True

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - [%(request_id)s] - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.addFilter(RequestIDFilter()) 
logger = logging.getLogger('loan_predictor') #logger will be injected into crud.py and services.py
logger.setLevel(logging.INFO)
logger.addHandler(handler)

load_resources(logger)

#FastAPI app
app = FastAPI()

"""
# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

# Middleware for request ID
@app.middleware('http')
async def add_request_id(request: Request, call_next):
    rid = str(uuid.uuid4())
    request.state.request_id = rid
    logger.info('Request started', extra={'request_id': rid})
    response = await call_next(request)
    response.headers['X-Request-ID'] = rid
    return response

# Health check\ @app.get('/')
def health_check():
    logger.info('Health check endpoint hit', extra={'request_id': 'health'})
    return {'message': 'Welcome to the Loan Approval Prediction API', 'status': 'Running'}

# Prediction endpoint
@app.post("/predict")
async def predict_endpoint(
    input_data: dict,
    request: Request
    #, db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Validates, preprocesses, predicts, saves to DB, and returns the result.
    """
    # Pydantic has already validated the payload
    logger.info("Prediction request received.")
    try:
        validate_payload(input_data.dict(), logger)
        # Preprocess input
        df = preprocess_input(input_data.dict(), logger)
        # Make prediction
        result = predict(df, logger)
        prediction = int(result["prediction"])
        confidence = float(result.get("confidence", 0.0))

        """
        # Save to DB
        new_pred = Prediction(
            request_id=request_id_ctx.get(),
            input_data=input_data.dict(),
            prediction_result=prediction
        )
        db.add(new_pred)
        db.commit()
        logger.info("Prediction saved to DB.")
        """

        # Return response
        status = "Approved" if prediction == 1 else "Rejected"
        return JSONResponse(
            status_code=200,
            content={
                "prediction": prediction,
                "confidence": confidence,
                "status": status
            }
        )

    except ValidationError as ve:
        # Should not occur: Pydantic handles request validation
        logger.error("Validation error: %s", ve)
        raise HTTPException(status_code=400, detail={"error": str(ve), "status": "Error"})
    except ValueError as ve:
        logger.error("Value error in prediction pipeline: %s", ve)
        raise HTTPException(status_code=400, detail={"error": str(ve), "status": "Error"})
    except Exception as e:
        logger.exception("Unexpected error in predict endpoint: %s", e)
        raise HTTPException(status_code=500, detail={"error": "Internal server error", "status": "Error"})

# Entry point for local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000)), log_level="info")
