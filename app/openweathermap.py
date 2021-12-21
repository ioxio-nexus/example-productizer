from typing import Any, Dict

import aiohttp
import orjson

from settings import conf


async def current_weather(lat: float, lon: float) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as client:
        opts = {
            "params": {
                "lat": str(lat),
                "lon": str(lon),
                "appid": conf.API_KEY.get_secret_value(),
            },
            "skip_auto_headers": ["user-agent"],
            "allow_redirects": False,
            "compress": True,
            "timeout": 30.0,
        }

        async with client.get(conf.API_ENDPOINT, **opts) as res:
            async with res:
                if res.status == 200:
                    return await res.json(loads=orjson.loads)
                else:
                    text = await res.text()
                    raise ValueError(f"OpenWeatherMap error {res.status}: {text}")

        raise ValueError("Request failed for some reason.")
