from fastapi import HTTPException, Header
from app.config import settings
import httpx
import jwt
from functools import lru_cache
import time

# Cache Clerk's JWKS to avoid repeated API calls
_jwks_cache = None
_jwks_cache_time = None

async def get_clerk_jwks():
    """Fetch Clerk's JWKS (JSON Web Key Set) for token verification."""
    global _jwks_cache, _jwks_cache_time
    
    # Cache for 1 hour
    if _jwks_cache and _jwks_cache_time and (time.time() - _jwks_cache_time) < 3600:
        return _jwks_cache
    
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.clerk.com/.well-known/jwks.json")
        if res.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch Clerk JWKS")
        _jwks_cache = res.json()
        _jwks_cache_time = time.time()
        return _jwks_cache


def get_public_key(token: str, jwks: dict) -> str:
    """Extract the public key from JWKS using the token's kid (key ID)."""
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    
    if not kid:
        raise HTTPException(status_code=401, detail="Invalid token: missing kid")
    
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    
    raise HTTPException(status_code=401, detail="Invalid token: kid not found in JWKS")


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Verify Clerk JWT and return user info."""
    if not authorization or not authorization.startswith("Bearer "):
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
            audience=settings.CLERK_PUBLISHABLE_KEY.split("_")[0] if settings.CLERK_PUBLISHABLE_KEY else None
        )
        
        # Extract user ID from token
        user_id = payload.get("sub")  # 'sub' is the subject (user ID) in Clerk tokens
        email = payload.get("email", "")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        return {
            "id": user_id,
            "email": email,
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
