from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.user import User
from app.models.account import Account
from typing import List

class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_all_accounts(self) -> List[Account]:
        result = await self.db.execute(select(Account))
        return result.scalars().all()