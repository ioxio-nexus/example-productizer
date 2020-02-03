from fastapi import APIRouter
from starlette.responses import UJSONResponse

from app.headers import X_SIGNATURE
from app.models import CurrentWeatherRequest, CurrentWeatherResponse
from app.openweathermap import current_weather
from app.utils import logger

router = APIRouter()


@router.post(
    "/Weather/Current/Metric",
    summary="Weather/Current/Metric Data Product",
    description="Current weather in metric units",
    response_model=CurrentWeatherResponse,
)
async def weather_current_metric(
    params: CurrentWeatherRequest, x_signature: str = X_SIGNATURE
):
    # TODO: Validate x_signature

    result = await current_weather(params.lat, params.lon)

    logger.info(f"Weather for %.2f, %.2f: %s", params.lat, params.lon, result)

    # https://openweathermap.org/weather-conditions
    main = result["weather"][0]["main"].lower()
    rain = "rain" in main or "drizzle" in main or "sleet" in main

    # https://openweathermap.org/current#current_JSON
    content = CurrentWeatherResponse(
        rain=rain,
        temp=result["main"]["temp"] - 273.15,  # Kelvin to Celsius
        pressure=result["main"]["pressure"],
        humidity=result["main"]["humidity"],
        windSpeed=result["wind"]["speed"],
        windDirection=result["wind"]["deg"],
    ).dict()

    return UJSONResponse(content=content, headers=response_headers)
