from dataclasses import dataclass
from typing import Optional

import jwt
from async_lru import alru_cache
from jwt import PyJWK
from yarl import URL

from app.utils import get_json, logger
from settings import API_TOKEN_LEEWAY, VALID_DATASPACES

# Some reasonable defaults for cache lifetimes for different stages of signature validation
#
# For production uses it would be a good idea to periodically fetch the JWKS file instead to avoid
# delays when data is being requested.

JWK_CACHE_TTL = 15 * 60  # Cache individual JWK for 15min
JWKS_CACHE_TTL = 60 * 60  # Cache entire JWKS file for 1 hour
JWKS_URL_CACHE_TTL = 24 * 60 * 60  # Cache determining JWKS URL for 24 hours


@dataclass
class DataspaceConfiguration:
    # https://docs.ioxio.dev/schemas/dataspace-configuration/

    authentication_providers: dict
    consent_providers: list[dict]
    dataspace_base_domain: str
    dataspace_name: str
    definition_viewer_url: str
    definitions: dict
    developer_portal_url: str
    docs_url: str
    jwks_uri: str  # TODO: This will be renamed _url
    product_gateway_url: str


@dataclass
class JWKResult:
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
    # x5t#S256 is an option, but it's not trivial to support here so leaving it out for now


@dataclass
class JWKSResult:
    # TODO: Link to JWKS file documentation
    keys: list[JWKResult]


@dataclass
class APIToken:
    # TODO: Link to IOXIO docs describing the token format
    iss: str  # Issuer base domain
    sub: str  # Group or app identification
    dsi: str  # Data source identifier for which this API token is valid
    exp: int  # Expiration time (unix timestamp)
    iat: int  # Issued at (unix timestamp)


@alru_cache(maxsize=16, ttl=JWKS_URL_CACHE_TTL)
async def determine_jwks_url(iss: str) -> str:
    """
    Fetch the issuer's dataspace configuration and determine the JWKS URL. We only support HTTPS schemes, which
    simplifies this a bit.

    :param iss: The base domain of the issuer
    :return: The JWKS URL from the dataspace configuration
    :raises HTTPStatusError: If the response from the server is not a successful one
    """

    # This file's format is documented at https://docs.ioxio.dev/schemas/dataspace-configuration/
    dataspace_configuration_url = str(
        URL.build(
            scheme="https",
            host=iss,
            path="/.well-known/dataspace/dataspace-configuration.json",
        )
    )

    logger.info(f"Fetching dataspace configuration from {dataspace_configuration_url}")
    result = await get_json(dataspace_configuration_url)

    dataspace_configuration = DataspaceConfiguration(**result)
    return dataspace_configuration.jwks_uri


@alru_cache(maxsize=16, ttl=JWKS_CACHE_TTL)
async def fetch_jwks(iss: str) -> (str, list[JWKResult]):
    """
    Figure out the issuer's JWKS URL and fetch the JWKS -hosted keys.

    :param iss: The base domain of the issuer
    :return: The JWKS URL from the dataspace configuration, and the keys hosted via JWKS
    :raises HTTPStatusError: If the response from the server is not a successful one
    """

    jwks_url = await determine_jwks_url(iss)

    logger.info(f"Fetching JWKS from {jwks_url}")
    result = await get_json(jwks_url)

    jwks = JWKSResult(keys=[JWKResult(**key) for key in result["keys"]])

    return jwks_url, jwks.keys


@alru_cache(maxsize=16, ttl=JWK_CACHE_TTL)
async def fetch_jwk(iss: str, kid: str) -> (str, PyJWK):
    """
    Fetch the JWK key 'kid' from the issuer's published JWKS. We also require it to be of type RSA, used for signing,
    and using RS256 algorithm.

    :param iss: Base domain of issuer, e.g. ioxio.com
    :param kid: Key ID in the JWKS, e.g. 302feac8851574f3ef74ec1c62a7489f
    :return:
    """
    jwks_url, jwks = await fetch_jwks(iss)
    for jwk in jwks:
        if (
            jwk.kty == "RSA"
            and jwk.use == "sig"
            and jwk.alg == "RS256"
            and jwk.kid == kid
        ):
            return jwks_url, PyJWK(jwk.__dict__)

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
    Parse the JWK issuer from the API token

    :param api_token: The JWT formatted API token
    :return: Issuer who created this JWT token
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
    """

    # Data sources are identified on dataspaces as <group> or <group>:<variant>, which on the DSI URI correspond to a
    # "user" and an optional "password"
    user, _, password = source.partition(":")  # Extract group:source to URL properties

    # Only add password property if it has a value, so we don't end up with an empty `:`
    extra = {}
    if password:
        extra["password"] = password

    # Use an URL builder to build the URI correctly
    dsi_url = URL.build(
        scheme="dpp",
        host=dataspace_base_domain,
        path=definition_path,
        user=user,
        **extra,
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

    # NOTE: If building for production use, verify that this DSI is one that you have intended to publish before making
    #       any requests.

    # Figure out the JWK that signed this token
    jwks_url, expected_signing_jwk = await fetch_jwk(dataspace_base_domain, kid)

    # This verifies signature and expiration time, then returns the payload
    jwt_payload = jwt.decode(
        jwt=api_token,
        leeway=API_TOKEN_LEEWAY,
        key=expected_signing_jwk.key,
        algorithms=["RS256"],
    )
    api_token = APIToken(**jwt_payload)

    if api_token.dsi != expected_dsi:
        raise Exception(f"Expected DSI {expected_dsi}, got {api_token.dsi}")

    logger.info(
        f"{api_token.sub} from {iss} accessing {api_token.dsi} with a valid API Token"
    )
