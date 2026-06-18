import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.account import Account
from app.models.transaction import Transaction
from app.core.cache import cache_balance, invalidate_balance_cache
from fastapi import HTTPException, status
from typing import List

class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def deposit(self, account: Account, amount: Decimal) -> dict:
        account.balance += amount
        transaction = Transaction(
            receiver_account_id=account.id,
            amount=amount,
            transaction_type="DEPOSIT",
            status="SUCCESS",
            description=f"Deposit of {amount}"
        )
        self.db.add(transaction)
        await self.db.flush()
        # Update cache
        await cache_balance(account.account_number, float(account.balance))
        return {
            "message": "Deposit successful",
            "amount": amount,
            "updated_balance": account.balance
        }

    async def transfer(self, sender_account: Account, receiver_account_number: str, amount: Decimal) -> dict:
        # Get receiver account with lock
        result = await self.db.execute(
            select(Account).where(Account.account_number == receiver_account_number).with_for_update()
        )
        receiver = result.scalar_one_or_none()
        if not receiver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver account not found")
        if sender_account.id == receiver.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot transfer to self")
        if sender_account.balance < amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

        # Perform transfer atomically (already within transaction)
        sender_account.balance -= amount
        receiver.balance += amount

        transaction = Transaction(
            sender_account_id=sender_account.id,
            receiver_account_id=receiver.id,
            amount=amount,
            transaction_type="TRANSFER",
            status="SUCCESS",
            description=f"Transfer to {receiver_account_number}"
        )
        self.db.add(transaction)
        await self.db.flush()

        # Invalidate caches
        await invalidate_balance_cache(sender_account.account_number)
        await invalidate_balance_cache(receiver.account_number)
        # Re-cache
        await cache_balance(sender_account.account_number, float(sender_account.balance))
        await cache_balance(receiver.account_number, float(receiver.balance))

        return {
            "message": "Transfer successful",
            "transaction_id": str(transaction.id),
            "amount": amount,
            "sender_balance": sender_account.balance
        }

    async def get_transaction_history(self, account_id: uuid.UUID) -> List[Transaction]:
        result = await self.db.execute(
            select(Transaction).where(
                (Transaction.sender_account_id == account_id) | (Transaction.receiver_account_id == account_id)
            ).order_by(Transaction.created_at.desc())
        )
        return result.scalars().all()

    async def get_transaction_detail(self, transaction_id: uuid.UUID, account_id: uuid.UUID) -> Transaction:
        result = await self.db.execute(select(Transaction).where(Transaction.id == transaction_id))
        txn = result.scalar_one_or_none()
        if not txn:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        if txn.sender_account_id != account_id and txn.receiver_account_id != account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return txn