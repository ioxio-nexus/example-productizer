from typing import Optional

import jwt
from async_lru import alru_cache
from jwt import PyJWK
from pydantic import BaseModel, Field
from yarl import URL

from app.utils import get_json, logger
from settings import API_TOKEN_LEEWAY, VALID_DATASPACES, VALID_DSIS

# Some reasonable defaults for cache lifetimes for different stages of signature validation
#
# For production uses it would be a good idea to periodically fetch the JWKS file instead to avoid
# delays when data is being requested.


JWK_CACHE_TTL = 15 * 60  # Cache individual JWK for 15 minutes
JWKS_CACHE_TTL = 60 * 60  # Cache entire JWKS file for 1 hour
JWKS_URL_CACHE_TTL = 24 * 60 * 60  # Cache determining JWKS URL for 24 hours


# NOTE: BaseModel -classes automatically discard extra properties, full contents may not be accurately described here


class DataspaceConfiguration(BaseModel):
    """
    Full structure documented at https://docs.ioxio.dev/schemas/dataspace-configuration/
    """

    jwks_url: str


class JWKResult(BaseModel):
    """
    A container for a single JSON Web Key

    https://datatracker.ietf.org/doc/html/rfc7517
    """

    alg: str
    e: str
    kid: str
    kty: str
    n: str
    use: str
    key_opts: Optional[list[str]] = None
    x5c: Optional[str] = None
    x5t: Optional[str] = None
    x5u: Optional[str] = None
    x5t_S256: Optional[str] = Field(None, alias="x5t#S256")


class JWKSResult(BaseModel):
    """
    Container for a jwks.json -file's contents

    https://stytch.com/blog/understanding-jwks/
    """

    keys: list[JWKResult]


class APIToken(BaseModel):
    # TODO: Link to IOXIO docs describing the token format, once docs exist

    iss: str  # Base URL of the dataspace that issued the API token
    sub: str  # Group or app identification
    aud: str  # Audience, the Data Source Identifier (DSI) for which this API token is valid
    exp: int  # Expiration time (unix timestamp)
    iat: int  # Issued at (unix timestamp)


@alru_cache(maxsize=16, ttl=JWKS_URL_CACHE_TTL)
async def determine_jwks_url(dataspace_base_domain: str) -> str:
    """
    Fetch the dataspace configuration and determine the JWKS URL. We only support HTTPS schemes, which simplifies this a
    bit.

    :param dataspace_base_domain: The base domain of the dataspace
    :return: The JWKS URL from the dataspace configuration
    :raises httpx.HTTPError: If the response from the server is not a successful one
    """

    # This file's format is documented at https://docs.ioxio.dev/schemas/dataspace-configuration/
    dataspace_configuration_url = str(
        URL.build(
            scheme="https",
            host=dataspace_base_domain,
            path="/.well-known/dataspace/dadef make_dsi(dataspace_base_domain: str, definition_path: str, source: str) -> str:
    """
    Construct a Data Source Identifier from the information on the request and token

    DSIs are URIs in the format: dpp://<source>@<dataspace_base_domain>/<data_definition>
    """

    # This function somewhat counterintuitively expects / -prefixed paths, so we'll just fix it for you if needed
    if not definition_path.startswith("/"):
        definition_path = f"/{definition_path}"

    # Data sources are identified on dataspaces as <group> or <group>:<variant>, which on the DSI URI correspond to a
    # "user" and an optional "password"
    user, _, password = source.partition(":")  # Extract group:source to URL properties

    if not password:
        # Passing the value None will not append it to the URL, whereas an empty string would be
        password = None

    # Use a URL builder to build the URI correctly
    #
    # Our expectation is that all the values are suitable for doing this with just string concatenation, however for
    # future proofing we want to do this a bit more carefully here.

    dsi_url = URL.build(
        scheme="dpp",
        host=dataspace_base_domain,
        path=definition_path,
        user=user,
        password=password,
    )

    return str(dsi_url)
taspace-configuration.json",
        )
    )

    logger.info(f"Fetching dataspace configuration from {dataspace_configuration_url}")
    result = await get_json(dataspace_configuration_url)

    dataspace_configuration = DataspaceConfiguration(**result)
    return dataspace_configuration.jwks_url


@alru_cache(maxsize=16, ttl=JWKS_CACHE_TTL)
async def fetch_jwks(dataspace_base_domain: str) -> (str, list[JWKResult]):
    """
    Figure out the dataspace's JWKS URL and fetch the JWKS -hosted keys.

    :param dataspace_base_domain: The base domain of the dataspace
    :return: The JWKS URL from the dataspace configuration, and the keys hosted via JWKS
    :raises httpx.HTTPError: If the response from the server is not a successful one
    """

    jwks_url = await determine_jwks_url(dataspace_base_domain)

    logger.info(f"Fetching JWKS from {jwks_url}")
    result = await get_json(jwks_url)

    jwks = JWKSResult(keys=[JWKResult(**key) for key in result["keys"]])

    return jwks_url, jwks.keys


@alru_cache(maxsize=16, ttl=JWK_CACHE_TTL)
async def fetch_jwk(dataspace_base_domain: str, kid: str) -> (str, PyJWK):
    """
    Fetch the JWK key 'kid' from the dataspace's published JWKS. We also require it to be of type RSA, used for signing,
    and using RS256 algorithm.

    :param dataspace_base_domain: Base domain of the dataspace, e.g. sandbox.ioxio-dataspace.com
    :param kid: Key ID in the JWKS, e.g. 302feac8851574f3ef74ec1c62a7489f
    :return: The JWKS URL the key was fetched from, as well as a PyJWK instance for the key
    :raises httpx.HTTPError: If the response from the server is not a successful one
    :raises Exception: If the key was not found
    """
    jwks_url, jwks = await fetch_jwks(dataspace_base_domain)
    for jwk in jwks:
        if (
            jwk.kty == "RSA"
            and jwk.use == "sig"
            and jwk.alg == "RS256"
            and jwk.kid == kid
        ):
            return jwks_url, PyJWK(jwk.dict(by_alias=True))

    # For proper durable operation, in case the JWKS content was fetched from cache and key was not found, we should
    # try to re-fetch fresh JWKS in case it is a newly added key.

    raise Exception(
        f"{jwks_url} does not contain a JWK with the ID {kid}, with kty RSA, use sig, and alg RS256. "
        f"Cannot verify API token."
    )


def get_kid(api_token) -> str:
    """
    Parse the JWK key ID from the API token

    :param api_token: The JWT formatted API token
    :return: Key ID used for signing this token
    :raises Exception: In case it was not possible to determine the key ID
    """
    jwt_headers = jwt.get_unverified_header(api_token)
    try:
        key_id: str = jwt_headers["kid"]
    except KeyError:
        raise Exception("Missing 'kid' in API token JWT header")

    return key_id


def get_iss(api_token) -> str:
    """
    Parse the JWK issuer from the API token. The issuer is the dataspace this API token is for.

    :param api_token: The JWT formatted API token
    :return: Issuer who created this JWT token, which is the dataspace base URL incl. protocol
    :raises Exception: In case it was not possible to determine the issuer
    """
    payload = jwt.decode(api_token, options={"verify_signature": False})
    try:
        issuer: str = payload["iss"]
    except KeyError:
        raise Exception("Missing 'iss' in API token JWT payload")

    return issuer


def make_dsi(dataspace_base_domain: str, definition_path: str, source: str) -> str:
    """
    Construct a Data Source Identifier from the information on the request and token

    DSIs are URIs in the format: dpp://<source>@<dataspace_base_domain>/<data_definition>
    """

    # This function somewhat counterintuitively expects / -prefixed paths, so we'll just fix it for you if needed
    if not definition_path.startswith("/"):
        definition_path = f"/{definition_path}"

    # Data sources are identified on dataspaces as <group> or <group>:<variant>, which on the DSI URI correspond to a
    # "user" and an optional "password"
    user, _, password = source.partition(":")  # Extract group:source to URL properties

    if not password:
        # Passing the value None will not append it to the URL, whereas an empty string would be
        password = None

    # Use a URL builder to build the URI correctly
    #
    # Our expectation is that all the values are suitable for doing this with just string concatenation, however for
    # future proofing we want to do this a bit more carefully here.

    dsi_url = URL.build(
        scheme="dpp",
        host=dataspace_base_domain,
        path=definition_path,
        user=user,
        password=password,
    )

    return str(dsi_url)


async def validate_api_token(api_token: str, definition_path: str, source: str):
    """
    Validate if the given API token is valid for the given Data Source Identifier at this moment

    :param api_token: The value of the X-API-Key header provided from the application, a JWT token
    :param definition_path: The path of the data product being processed /Data/Product_v1.0
    :param source: The "source" is expected as a query parameter ?source=example
    :raises Exception: If validation fails in general, e.g. requests time out
    :raises pyjwt.JWTError: If there are issues with the JWT token itself
    :raises httpx.HTTPError: If the HTTP responses during JWKS resolution are not successful
    """

    # Parse the key ID and issuer from the API token needed to verify the signature
    kid = get_kid(api_token)
    iss = get_iss(api_token)
    dataspace_base_domain = iss.removeprefix("https://")

    if dataspace_base_domain not in VALID_DATASPACES:
        raise Exception(
            f"Unknown dataspace {iss}, only supporting {', '.join(VALID_DATASPACES)}. Check settings.py"
        )

    # Build the DSI that matches this request, to check that it matches expectation
    expected_dsi = make_dsi(dataspace_base_domain, definition_path, source)

    # NOTE: If building for production use, you need to get the expected DSI value from the dataspace developer portal
    # for your data source, and verify the value above matches it exactly before continuing the processing here. If you
    # do not verify the DSI, it is feasible for a 3rd party to register your API as another data source on the
    # dataspace, and have the dataspace generate valid API tokens for it, which will pass the validation logic below.

    if VALID_DSIS:
        if expected_dsi not in VALID_DSIS:
            raise Exception(f"DSI {expected_dsi}, is not valid for this service.")

    # Figure out the JWK that signed this token
    jwks_url, expected_signing_jwk = await fetch_jwk(dataspace_base_domain, kid)

    # This verifies signature and expiration time, then returns the payload
    try:
        jwt_payload = jwt.decode(
            jwt=api_token,
            leeway=API_TOKEN_LEEWAY,
            key=expected_signing_jwk.key,
            algorithms=["RS256"],
        )
    except jwt.exceptions.InvalidSignatureError as e:
        raise Exception(
            f"API Token signature cannot be verified with the key {kid} fetched from {jwks_url}"
        ) from e

    api_token = APIToken(**jwt_payload)

    if api_token.aud != expected_dsi:
        raise Exception(f"Expected DSI {expected_dsi}, got {api_token.aud}")

    logger.info(
        f"{api_token.sub} from {iss} accessing {api_token.aud} with a valid API Token"
    )
