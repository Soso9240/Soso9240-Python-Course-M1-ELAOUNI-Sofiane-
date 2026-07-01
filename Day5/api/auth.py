"""API key authentication for protected routes.

The expected key is read from the API_KEY environment variable.
Clients must send it in the `X-API-Key` header.
"""

import os

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Depends(_api_key_header)) -> str:
    """FastAPI dependency that validates the X-API-Key header.

    Raises HTTP 403 if the header is missing or does not match the
    API_KEY environment variable.
    """
    expected = os.getenv("API_KEY")

    if not expected:
        # Misconfiguration: the server itself has no API_KEY set.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server is missing API_KEY configuration",
        )

    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )

    return api_key
