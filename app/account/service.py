import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.account import Account
from app.core.cache import get_cached_balance, cache_balance
from fastapi import HTTPException, status
import random
import string

class AccountService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(self, user_id: uuid.UUID) -> Account:
        # Check if user already has an account (one account per user)
        result = await self.db.execute(select(Account).where(Account.user_id == user_id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has an account")
        # Generate unique account number (simplified)
        account_number = await self._generate_account_number()
        account = Account(user_id=user_id, account_number=account_number, balance=0)
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def _generate_account_number(self) -> str:
        # Simplified: ACC + random digits, ensure uniqueness
        while True:
            digits = ''.join(random.choices(string.digits, k=6))
            acc_num = f"ACC{digits}"
            result = await self.db.execute(select(Account).where(Account.account_number == acc_num))
            if not result.scalar_one_or_none():
                return acc_num

    async def get_my_account(self, user_id: uuid.UUID) -> Account:
        result = await self.db.execute(select(Account).where(Account.user_id == user_id))
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return account

    async def get_balance(self, account: Account) -> dict:
        # Try cache
        cached = await get_cached_balance(account.account_number)
        if cached is not None:
            return {"account_number": account.account_number, "balance": cached}
        # Refresh from DB
        await self.db.refresh(account)
        balance = account.balance
        await cache_balance(account.account_number, float(balance))
        return {"account_number": account.account_number, "balance": balance}