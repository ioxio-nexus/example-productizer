from fastapi import Header

X_SIGNATURE = Header(
    default=None,
    title="Request signature",
    description="HMAC-RSA256 signature for the request using Product Gateway's public key",
)
