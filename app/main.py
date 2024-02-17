from fastapi import FastAPI
from app.routers import dataproduct

app = FastAPI(
    title="Productizer",
    description="Productizer for the Weather/Current/Metric_v1.0 Data Product",
    version="1.0.0",
)

app.include_router(dataproduct.router)
