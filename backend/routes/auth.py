from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.services.db_service import db_service

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


class SignupRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    name: str


class UserProfile(BaseModel):
    user_id: str
    email: str
    name: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await db_service.find_one("users", {"_id": payload.get("sub")})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/signup", response_model=AuthResponse)
async def signup(payload: SignupRequest):
    existing = await db_service.find_one("users", {"email": payload.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user_doc = {
        "email": payload.email,
        "password": hash_password(payload.password),
        "name": payload.name or payload.email.split("@")[0],
        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
    }
    user_id = await db_service.insert_one("users", user_doc)
    if user_id is None:
        import uuid
        user_id = str(uuid.uuid4())
    token = create_access_token({"sub": user_id, "email": payload.email})
    return AuthResponse(
        token=token,
        user_id=user_id,
        email=payload.email,
        name=user_doc["name"],
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    user = await db_service.find_one("users", {"email": payload.email})
    if not user or not verify_password(payload.password, user.get("password", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user["_id"]), "email": payload.email})
    return AuthResponse(
        token=token,
        user_id=str(user["_id"]),
        email=payload.email,
        name=user.get("name", ""),
    )


@router.get("/me", response_model=UserProfile)
async def get_profile(user: dict = Depends(get_current_user)):
    return UserProfile(
        user_id=str(user["_id"]),
        email=user.get("email", ""),
        name=user.get("name", ""),
    )
