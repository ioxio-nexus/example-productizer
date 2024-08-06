import logging

import httpx

logger = logging.getLogger("uvicorn")


async def get_json(url) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)

        # If the response is not with a successful status code throw an exception
        response.raise_for_status()

        return response.json()
