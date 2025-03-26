import requests
from fastapi import APIRouter, Header, HTTPException, Depends

from app.config import SUPABASE_URL

router = APIRouter()


def get_current_user(authorization: str = Header(None)):
    """Validate JWT Token with Supabase."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Header")

    token = authorization.split("Bearer ")[1]
    response = requests.get(
        f"{SUPABASE_URL}/auth/v1/user", headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Token")

    return response.json()


@router.get("/me")
async def get_user(user: dict = Depends(get_current_user)):
    """Returns authenticated user data."""
    return user
