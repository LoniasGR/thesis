from fastapi import FastAPI, Request, status, Depends

import models.schemas as schemas
import db.models as models
import db.crud as crud
import client.client as services
from logger.logger import CustomLogger
from db.database import SessionLocal, engine
from client.client import create_side_by_side

models.Base.metadata.create_all(bind=engine)
logger: CustomLogger = CustomLogger(__name__)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/comparison", response_model=schemas.ComparisonSuggestion)
def get_comparison(request: Request, db=Depends(get_db)):
    host = request.headers["Host"]
    if "x-forwared-for" in request.headers:
        host = request.headers["x-forwared-for"]

    client = crud.create_or_get_client(db, host=host)
    suggestion = services.create_side_by_side(db)

    crud.create_suggestion(db, suggestion, client)

    return suggestion


@app.post("/selection")
def post_selection():
    pass


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=schemas.HealthCheck,
)
def get_health() -> schemas.HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return schemas.HealthCheck(status="OK")
