from fastapi import HTTPException, Header
from app.config import settings
import httpx
import jwt
import time
import logging

logger = logging.getLogger(__name__)

# Cache Clerk's JWKS to avoid repeated API calls
_jwks_cache = None
_jwks_cache_time = None

async def get_clerk_jwks():
    """Fetch Clerk's JWKS (JSON Web Key Set) for token verification."""
    global _jwks_cache, _jwks_cache_time
    
    # Cache for 1 hour
    if _jwks_cache and _jwks_cache_time and (time.time() - _jwks_cache_time) < 3600:
        return _jwks_cache
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=True) as client:
            res = await client.get(
                "https://api.clerk.com/.well-known/jwks.json",
                headers={"User-Agent": "AI-Finance-Operator/1.0"}
            )
            if res.status_code != 200:
                logger.error(f"Failed to fetch Clerk JWKS: {res.status_code} {res.text}")
                raise HTTPException(status_code=500, detail=f"Clerk JWKS fetch failed: {res.status_code}")
            
            _jwks_cache = res.json()
            _jwks_cache_time = time.time()
            logger.info("Successfully fetched Clerk JWKS")
            return _jwks_cache
    except httpx.RequestError as e:
        logger.error(f"Network error fetching Clerk JWKS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reach Clerk: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching Clerk JWKS: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Clerk JWKS: {str(e)}")


def get_public_key(token: str, jwks: dict):
    """Extract the public key from JWKS using the token's kid (key ID)."""
    try:
        headers = jwt.get_unverified_header(token)
    except jwt.DecodeError as e:
        logger.error(f"Invalid token header: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    kid = headers.get("kid")
    
    if not kid:
        logger.error("Token missing 'kid' in header")
        raise HTTPException(status_code=401, detail="Invalid token: missing key ID")
    
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            try:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
            except Exception as e:
                logger.error(f"Failed to parse public key: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to parse public key")
    
    logger.error(f"Key ID {kid} not found in Clerk JWKS")
    raise HTTPException(status_code=401, detail="Invalid token: key not found")


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Verify Clerk JWT and return user info."""
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        # Get Clerk's JWKS
        jwks = await get_clerk_jwks()
        public_key = get_public_key(token, jwks)
        
        # Verify and decode the JWT
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False}  # Don't verify audience - Clerk tokens may not have it
        )
        
        # Extract user ID from token
        user_id = payload.get("sub")  # 'sub' is the subject (user ID) in Clerk tokens
        email = payload.get("email", "")
        
        if not user_id:
            logger.error("Token missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        logger.info(f"User {user_id} authenticated successfully")
        return {
            "id": user_id,
            "email": email,
        }
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
