from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.routers import dataproduct, health

app = FastAPI(
    title="Productizer",
    description="Productizer for the OpenWeatherMap API",
    version="1.0.0",
    default_response_class=ORJSONResponse,
)

app.include_router(health.router)
app.include_router(dataproduct.router)
