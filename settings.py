# Which dataspace base URLs are considered valid for API tokens - i.e. where have you published this source.
# If you publish the source on a dataspace that is not on this list, API token validation will fail.
VALID_DATASPACES = ["sandbox.ioxio-dataspace.com", "testbed.fi"]

# How long do we allow expired API tokens to be used to account for clock drift, delays and so on. The default lifetime
# is 1h so 60s seems like a pretty reasonable value.
API_TOKEN_LEEWAY = 60  # Seconds
