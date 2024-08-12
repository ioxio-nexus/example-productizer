from typing import Optional

from fastapi import Header, Request

from app.api_tokens import validate_api_token


async def verify_api_token(
    request: Request,
    x_api_key: Optional[str] = Header(
        None, title="API token for accessing this source"
    ),
    source: Optional[str] = "",
):
    """
    A FastAPI dependency that will validate the X-API-Key header if it's present, without requiring it to be present. Please note that if you plan to base your API token verification upon this code.

    :param request: The request.url.path is expected to be the data product path, if you have some other base path, make sure you trim it.
    :param x_api_key: The X-API-Key header to (optionally) be verified.
    :param source: Expected as a query parameter ?source=example
    :raises Exception: In case validation fails
    """

    # We consider X-API-Key always optional here, you can change the code to require it, or choose to trust that the
    # configuration on the Product Gateway does not allow requests without an API token through if you have configured
    # it to be required for your data source.
    if x_api_key is None:
        return

    # This will throw an exception and not process the request further if validation fails
    await validate_api_token(x_api_key, request.url.path, source)
