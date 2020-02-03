from fastapi import FastAPI

from app.routers import health, dataproduct

app = FastAPI(
    title="Productizer",
    description="Productizer for the OpenWeatherMap API",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(dataproduct.router)
