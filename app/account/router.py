from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.account.schemas import AccountCreateResponse, AccountResponse, BalanceResponse
from app.account.service import AccountService
from app.core.dependencies import get_db, get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=AccountCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AccountService(db)
    account = await service.create_account(current_user.id)
    return {
        "id": str(account.id),
        "user_id": str(account.user_id),
        "account_number": account.account_number,
        "balance": account.balance
    }

@router.get("/me", response_model=AccountResponse)
async def get_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AccountService(db)
    account = await service.get_my_account(current_user.id)
    return {
        "id": str(account.id),
        "user_id": str(account.user_id),
        "account_number": account.account_number,
        "created_at": account.created_at.isoformat(),
        "updated_at": account.updated_at.isoformat()
    }

@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AccountService(db)
    account = await service.get_my_account(current_user.id)
    return await service.get_balance(account)