from logging import getLogger

import httpx

logger = getLogger("__name__")


async def get_json(url) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        # If the response is not with a successful status code throw an exception
        response.raise_for_status()

        return response.json()
