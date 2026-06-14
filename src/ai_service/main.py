"""
IoT Ingestion API for Lab 05.

Endpoints:
- POST /readings          – create a new sensor reading
- GET  /readings          – list all readings (optionally filter by sensor_id)
- GET  /readings/{id}     – get a single reading by ID
- GET  /health            – health check
"""

from fastapi import FastAPI, HTTPException, status, Request, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import http

# ------------------------------
# Configuration
# ------------------------------
APP_NAME = "IoT Ingestion API"
APP_VERSION = "0.5.0"
AUTH_TOKEN = "local-dev-token"          # default, can be overridden by env

# ------------------------------
# Pydantic models
# ------------------------------
class ReadingCreate(BaseModel):
    sensor_id: str = Field(..., example="sensor_01")
    value: float = Field(..., example=25.5)
    unit: str = Field(..., example="celsius")

class ReadingResponse(BaseModel):
    id: str
    sensor_id: str
    value: float
    unit: str
    timestamp: datetime

# ------------------------------
# In‑memory storage (for demo)
# ------------------------------
readings_db: Dict[str, Dict[str, Any]] = {}

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="API for ingesting sensor readings",
)

# ------------------------------
# Helper: get status message (safe replacement for HTTP_STATUS_CODES)
# ------------------------------
def get_status_message(code: int) -> str:
    try:
        return http.HTTPStatus(code).phrase
    except ValueError:
        return "Unknown"

# ------------------------------
# Exception handler (safe version)
# ------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "status_message": get_status_message(exc.status_code),
        },
        headers=getattr(exc, "headers", None),
    )

# ------------------------------
# Dependencies
# ------------------------------
async def verify_token(x_token: str = Header(...)):
    if x_token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return x_token

# ------------------------------
# Health endpoint
# ------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}

# ------------------------------
# API endpoints
# ------------------------------
@app.post("/readings", response_model=ReadingResponse, status_code=201)
async def create_reading(
    reading: ReadingCreate,
    token: str = Depends(verify_token)
):
    reading_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    stored = reading.dict()
    stored["id"] = reading_id
    stored["timestamp"] = now
    readings_db[reading_id] = stored
    return ReadingResponse(id=reading_id, **stored)

@app.get("/readings", response_model=List[ReadingResponse])
async def list_readings(
    sensor_id: Optional[str] = None,
    token: str = Depends(verify_token)
):
    result = []
    for item in readings_db.values():
        if sensor_id and item["sensor_id"] != sensor_id:
            continue
        result.append(ReadingResponse(**item))
    return result

@app.get("/readings/{reading_id}", response_model=ReadingResponse)
async def get_reading(
    reading_id: str,
    token: str = Depends(verify_token)
):
    if reading_id not in readings_db:
        raise HTTPException(status_code=404, detail="Reading not found")
    return ReadingResponse(**readings_db[reading_id])

# ------------------------------
# Run directly (for development)
# ------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)