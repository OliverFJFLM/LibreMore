from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas
from ..deps import create_access_token, get_current_user, get_db, get_password_hash, verify_password
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(payload: schemas.UserCreate, session: AsyncSession = Depends(get_db)) -> dict:
    existing = await session.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=payload.email, password_hash=get_password_hash(payload.password))
    session.add(user)
    await session.commit()
    return {"ok": True}


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
) -> schemas.TokenResponse:
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)}, expires_delta=timedelta(hours=12))
    return schemas.TokenResponse(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
async def me(current_user: User = Depends(get_current_user)) -> schemas.UserOut:
    return schemas.UserOut(id=current_user.id, email=current_user.email, created_at=current_user.created_at)
