from pydantic import BaseSettings, HttpUrl, SecretStr


class Settings(BaseSettings):
    # OpenWeatherMap.org API key
    API_KEY: SecretStr = ""

    # API endpoint to use
    API_ENDPOINT: HttpUrl = "https://api.openweathermap.org/data/2.5/weather"

    class Config:
        env_file = ".env"


conf = Settings()
