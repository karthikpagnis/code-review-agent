"""
Entra ID (Azure AD) JWT validation middleware.

Flow:
  1. Frontend logs in via MSAL.js → gets access token
  2. Frontend sends token as  Authorization: Bearer <token>
  3. This module fetches Microsoft's public JWKS and validates the token
  4. FastAPI routes declare  current_user: str = Depends(get_current_user)
"""

import os
import httpx
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError, ExpiredSignatureError

TENANT_ID = os.getenv("TENANT_ID", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
JWKS_URI  = f"{AUTHORITY}/discovery/v2.0/keys"
ISSUER    = f"{AUTHORITY}/v2.0"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{AUTHORITY}/oauth2/v2.0/authorize",
    tokenUrl=f"{AUTHORITY}/oauth2/v2.0/token",
    scopes={"api://{CLIENT_ID}/review.read": "Submit code for review"},
)


@lru_cache(maxsize=1)
def get_jwks() -> dict:
    """Cache Microsoft's public keys — refreshed on process restart."""
    response = httpx.get(JWKS_URI, timeout=10)
    response.raise_for_status()
    return response.json()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Validate the Bearer JWT from Entra ID.
    Returns the decoded token payload (contains 'preferred_username', 'oid', etc.)
    Raises HTTP 401 on any validation failure.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwks = get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=ISSUER,
            options={"verify_exp": True},
        )
        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired — please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
