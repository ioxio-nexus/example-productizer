from typing import Optional

from fastapi import Header, Request

from app.api_tokens import validate_api_token
from app.utils import logger


async def verify_api_token(
    request: Request,
    x_api_key: Optional[str] = Header(
        None, title="API token for accessing this source"
    ),
    source: Optional[str] = "",
):
    """
    The "source" is expected as a query parameter ?source=example
    The request path is expected to be the data product path, if you have some other base path, make sure you trim it.

    :param request:
    :param x_api_key:
    :param source:
    :raises Exception: In case validation fails
    """

    # We consider X-API-Key always optional here, you can change the code to require it, or choose to trust that the
    # configuration on the Product Gateway does not allow requests without an API token through if you have configured
    # it to be required for your data source.
    if x_api_key is None:
        return

    token = await validate_api_token(x_api_key, request.url.path, source)
    logger.debug("Received valid API token", token=token)
