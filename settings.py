# OpenWeatherMap.org API key
API_KEY = ""

# API endpoint to use
API_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"

try:
    from settings_local import *
except ImportError:
    pass
