from fastapi import HTTPException, Header
from app.config import settings
from jose import jwt, JWTError
import logging

logger = logging.getLogger(__name__)


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Verify Clerk JWT using secret key and return user info."""
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        # Decode and verify JWT using Clerk's secret key
        # Clerk tokens use HS256 algorithm with the secret key
        payload = jwt.decode(
            token,
            settings.CLERK_SECRET_KEY,
            algorithms=["HS256"],
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
    
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid or expired token")
    except Exception as e:
        logger.error(f"Unexpected authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
