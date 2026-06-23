from fastapi import HTTPException, Header
from app.config import settings
import httpx

async def get_current_user(authorization: str = Header(None)) -> dict:
    """Verify Clerk JWT and return user info."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]

    # Verify token with Clerk
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.clerk.com/v1/tokens/verify",
            params={"token": token},
            headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"},
        )

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    data = res.json()
    return {
        "id":    data.get("sub") or data.get("user_id"),
        "email": data.get("email", ""),
    }
