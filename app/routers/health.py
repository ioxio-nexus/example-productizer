from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: bool


@router.get("/health", response_model=HealthResponse)
async def healthcheck():
    return HealthResponse(status=True)
