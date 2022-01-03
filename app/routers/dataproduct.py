from fastapi import APIRouter

from app.models import CurrentWeatherMetricRequest, CurrentWeatherMetricResponse
from app.openweathermap import get_current_weather
from app.utils import logger

router = APIRouter()


@router.post(
    "/Weather/Current/Metric",
    summary="Weather/Current/Metric Data Product",
    description="Current weather in metric units",
    response_model=CurrentWeatherMetricResponse,
)
async def weather_current_metric(params: CurrentWeatherMetricRequest):

    result = await get_current_weather(params.lat, params.lon)

    logger.info("Weather for %.2f, %.2f: %s", params.lat, params.lon, result)

    # https://openweathermap.org/weather-conditions
    main = result["weather"][0]["main"].lower()
    rain = "rain" in main or "drizzle" in main or "sleet" in main

    # https://openweathermap.org/current#current_JSON
    return CurrentWeatherMetricResponse(
        rain=rain,
        temp=result["main"]["temp"] - 273.15,  # Kelvin to Celsius
        pressure=result["main"]["pressure"],
        humidity=result["main"]["humidity"],
        wind_speed=result["wind"]["speed"],
        wind_direction=result["wind"]["deg"],
    )
