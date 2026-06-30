from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.schemas import UserRegister, AuthMeResponse
from app.auth.service import AuthService
from app.auth.dependencies import rate_limit_login
from app.core.dependencies import get_db, get_current_user
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register(data)
    return {"message": "User registered successfully", "user_id": str(user.id)}

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_login),
):
    service = AuthService(db)
    token = await service.login(form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=AuthMeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.get_me(current_user.id)
    new_token = create_access_token(
        {"user_id": str(user.id), "email": user.email, "role": user.role}
    )
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_active": user.is_active,
        "jwt": new_token,
    }