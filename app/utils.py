import logging

import httpx

logger = logging.getLogger("uvicorn")


async def get_json(url: str) -> dict:
    """
    Fetch a JSON file's contents as a Python dict, raise exception in case of any errors

    :param url: The request URL
    :return: Parsed JSON
    :raises httpx.HTTPError: In case of any errors during the request
    """
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url)

        # If the response is not with a successful status code throw an exception
        response.raise_for_status()

        return response.json()
