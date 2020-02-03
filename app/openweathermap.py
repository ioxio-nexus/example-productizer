from typing import Dict, Any

import aiohttp
import ujson

from settings import API_KEY, API_ENDPOINT


async def current_weather(lat: float, lon: float) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as client:
        opts = {
            "params": {"lat": str(lat), "lon": str(lon), "appid": API_KEY},
            "skip_auto_headers": ["user-agent"],
            "allow_redirects": False,
            "compress": True,
            "timeout": 30.0,
        }

        async with client.get(API_ENDPOINT, **opts) as res:
            async with res:
                if res.status == 200:
                    return await res.json(loads=ujson.loads)

        raise ValueError("Request failed for some reason.")
