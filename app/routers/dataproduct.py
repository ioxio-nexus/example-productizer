from fastapi import APIRouter

from app.models import CurrentWeatherMetricRequest, CurrentWeatherMetricResponse
from app.utils import logger
import random

router = APIRouter()


@router.post(
    "/Weather/Current/Metric_v1.0",
    summary="Current weather in a given location",
    description="Common data points about the current weather with metric units in a "
                "given location. Simplified for example use,"
                " and not following industry standards.",
    response_model=CurrentWeatherMetricResponse,
)
def get_weather_for_coords(params: CurrentWeatherMetricRequest):

    logger.info(f"Fetching weather for {params.lat}, {params.lon}")

    humidity = min(random.uniform(0, 125), 100)  # nosec
    rain = humidity >= 99
    return CurrentWeatherMetricResponse(
        rain=rain,
        temp=random.uniform(-30, 40),  # nosec
        pressure=random.uniform(870, 1083.8),  # nosec
        humidity=humidity,
        wind_speed=random.uniform(0, 100),  # nosec
        wind_direction=random.uniform(0, 360),  # nosec
    )
