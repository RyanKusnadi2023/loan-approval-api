import os
import uuid
import logging
from contextvars import ContextVar

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pydantic import ValidationError

from database.base import Base
from .services import load_resources, preprocess_input, predict
from .schemas import LoanApplication, validate_payload
from .crud import init_db, create_db

# ——— Context var to hold the request ID for the current execution context ———
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="N/A")

# ——— Load env & resources ———
load_dotenv()

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

# Load resources like models, encoders, etc.
load_resources(logging.getLogger("loan_predictor"))
init_db()
create_db()

# ——— Middleware to generate & store a new request ID per incoming request ———
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 1) Generate & store request ID
    rid = str(uuid.uuid4())
    request.state.request_id = rid
    request_id_ctx.set(rid)

    client = request.client
    http_ver = request.scope.get("http_version", "1.1")

    try:
        # 2) Call the downstream handler
        response: Response = await call_next(request)
    except HTTPException as exc:
        # 3a) If an HTTPException bubbles up, log with its detail
        logger.error(
            f'{client.host}:{client.port} - "{request.method} {request.url.path} HTTP/{http_ver}" '
            f'{exc.status_code} - {exc.detail}',
            extra={"request_id": rid}
        )
        # re-raise so FastAPI still returns the correct error response
        raise

    # 3b) For non-exception responses, build a base log message
    base = (
        f'{client.host}:{client.port} - '
        f'"{request.method} {request.url.path} HTTP/{http_ver}" '
        f'{response.status_code}'
    )

    if response.status_code >= 400:
        # Try to grab the body text as “description”
        try:
            # Note: this only works if response.body() is available;
            # streaming responses will need a different approach.
            body_bytes = await response.body()
            desc = body_bytes.decode(errors="ignore")
        except Exception:
            desc = "<unable to read body>"

        logger.error(f"{base} - {desc}", extra={"request_id": rid})
    else:
        logger.info(base, extra={"request_id": rid})

    # 4) Attach the header & return
    response.headers["X-Request-ID"] = rid
    return response


# ——— Health check ———
@app.get("/")
def health_check():
    logger.info("Health check endpoint hit")
    return {"message": "Welcome to the Loan Approval Prediction API", "status": "Running"}

@app.post("/predict")
async def predict_endpoint(input_data: LoanApplication, request: Request) -> JSONResponse:
    """
    Validates, preprocesses, predicts, saves to DB, and returns the result.
    """
    logger.info("Prediction request received.")

    # 1. Explicit payload validation
    is_valid, errors = validate_payload(input_data.model_dump(), logger)
    if not is_valid:
        # abort early on validation errors
        raise HTTPException(
            status_code=400,
            detail={"error": errors, "status": "Error"}
        )

    try:
        # 2. Preprocess & predict
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

    except ValueError as ve:
        logger.error("Value error in prediction pipeline: %s", ve)
        raise HTTPException(
            status_code=400,
            detail={"error": str(ve), "status": "Error"}
        )
    except Exception as e:
        logger.exception("Unexpected error in predict endpoint: %s", e)
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "status": "Error"}
        )
    

# ——— Entry point for local development ———
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        log_level="info",
        access_log=False
    )