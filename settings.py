# Which dataspace base URLs are considered valid for API tokens - i.e. where have you published this source.
# If you publish the source on a dataspace that is not on this list, API token validation will fail.
VALID_DATASPACES = ["sandbox.ioxio-dataspace.com", "testbed.fi"]

# Set to None to bypass DSI validation
VALID_DSIS = None

# If set to a list, requires any API token DSI to be on the list. Should be done for production-like use.
# VALID_DSIS = ["dpp://example@sandbox.ioxio-dataspace.com/Weather/Current/Metric_v1.0"]

# How long do we allow expired API tokens to be used to account for clock drift, delays and so on. The default lifetime
# is 1h so 60s seems like a pretty reasonable value.
API_TOKEN_LEEWAY = 60  # Seconds
