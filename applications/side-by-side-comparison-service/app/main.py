from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import models.schemas as schemas
import db.models as models
import db.crud as crud
import client.client as services
from logger.logger import CustomLogger
from db.database import SessionLocal, engine
from fastapi.exceptions import HTTPException

from utils.utils import getHost

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


@app.get("/comparison", response_model=schemas.ComparisonSuggestion)
def get_comparison(request: Request, db=Depends(get_db)):
    host = getHost(request.headers)

    client = crud.create_or_get_client(db, host=host)
    suggestion = services.create_side_by_side(db)

    crud.create_suggestion(db, suggestion, client)

    return suggestion


@app.post("/selection")
def post_selection(cmp: schemas.ComparisonBase, db=Depends(get_db)):
    new_ev = crud.update_comparison_answer(db, cmp.uuid, cmp.response)
    if new_ev == None:
        raise HTTPException(status_code=400, detail="Wrong evaluation id")
    return new_ev


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


app.mount("/", SPAStaticFiles(directory="frontend/dist", html=True), name="app")
