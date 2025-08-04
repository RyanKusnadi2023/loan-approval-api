import os
import uuid
import logging
from contextvars import ContextVar

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import ValidationError

from .services import load_resources, preprocess_input, predict
from .schemas import LoanApplication, validate_payload

# ——— Context var to hold the request ID for the current execution context ———
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="N/A")

# ——— Load env & resources ———
load_dotenv()
load_resources(logging.getLogger("loan_predictor"))

# ——— Logging setup with filter that draws from our ContextVar ———
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - [%(request_id)s] - %(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.addFilter(RequestIDFilter())

logger = logging.getLogger("loan_predictor")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ——— FastAPI app ———
app = FastAPI()

# ——— Middleware to generate & store a new request ID per incoming request ———
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = str(uuid.uuid4())
    # set both in request.state (if you need it elsewhere) and in ContextVar
    request.state.request_id = rid
    request_id_ctx.set(rid)

    logger.info("Request started")
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

# ——— Health check ———
@app.get("/")
def health_check():
    logger.info("Health check endpoint hit")
    return {"message": "Welcome to the Loan Approval Prediction API", "status": "Running"}

# ——— Prediction endpoint ———
@app.post("/predict")
async def predict_endpoint(input_data: LoanApplication, request: Request) -> JSONResponse:
    """
    Validates, preprocesses, predicts, saves to DB, and returns the result.
    """
    logger.info("Prediction request received")
    try:
        # Payload validation
        validate_payload(input_data.model_dump(), logger)

        # Preprocess & predict
        df = preprocess_input(input_data.model_dump(), logger)

        result = predict(df, logger)
        prediction = int(result["prediction"])
        confidence = float(result.get("confidence", 0.0))

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
        logger.error("Validation error: %s", ve)
        raise HTTPException(status_code=400, detail={"error": str(ve), "status": "Error"})
    except ValueError as ve:
        logger.error("Value error in prediction pipeline: %s", ve)
        raise HTTPException(status_code=400, detail={"error": str(ve), "status": "Error"})
    except Exception as e:
        logger.exception("Unexpected error in predict endpoint: %s", e)
        raise HTTPException(status_code=500, detail={"error": "Internal server error", "status": "Error"})

# ——— Entry point for local development ———
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
