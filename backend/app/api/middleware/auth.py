from fastapi import HTTPException, Header
from app.config import settings
import httpx
import jwt
import time
from typing import Dict, Optional

# Cache Clerk JWKS for performance
_jwks_cache: Optional[Dict] = None
_jwks_cache_time: Optional[float] = None


async def get_clerk_jwks():
    """
    Fetch Clerk JWKS (JSON Web Key Set).
    Cached for 1 hour.
    """
    global _jwks_cache, _jwks_cache_time

    # Return cached keys if valid
    if (
        _jwks_cache
        and _jwks_cache_time
        and (time.time() - _jwks_cache_time) < 3600
    ):
        return _jwks_cache

    try:
        clerk_jwks_url = f"{settings.CLERK_JWT_ISSUER}/.well-known/jwks.json"

        async with httpx.AsyncClient() as client:
            response = await client.get(clerk_jwks_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch Clerk JWKS"
            )

        _jwks_cache = response.json()
        _jwks_cache_time = time.time()

        return _jwks_cache

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load Clerk JWKS: {str(e)}"
        )


def get_public_key(token: str, jwks: dict):
    """
    Extract correct public key from Clerk JWKS using JWT kid.
    """
    try:
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")

        if not kid:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing kid"
            )

        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)

        raise HTTPException(
            status_code=401,
            detail="Invalid token: public key not found"
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token parsing failed: {str(e)}"
        )


async def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Validate Clerk JWT and return authenticated user.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization format"
        )

    token = authorization.split(" ")[1]

    try:
        # Fetch Clerk JWKS
        jwks = await get_clerk_jwks()

        # Extract correct public key
        public_key = get_public_key(token, jwks)

        # Decode and verify JWT
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": False,  # disable audience check for now
            },
        )

        # Extract user details
        user_id = payload.get("sub")
        email = payload.get("email", "")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID"
            )

        return {
            "id": user_id,
            "email": email,
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )
