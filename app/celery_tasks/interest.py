from app.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.account import Account
from app.models.transaction import Transaction
from sqlmodel import select
import asyncio
from decimal import Decimal
from app.core.config import settings

async def _calculate_interest():
    async with async_session_factory() as db:
        # Fetch all accounts with lock to avoid race
        result = await db.execute(select(Account).with_for_update())
        accounts = result.scalars().all()
        for account in accounts:
            interest = account.balance * Decimal(settings.INTEREST_APPLY_RATE / 100)
            account.balance += interest
            txn = Transaction(
                receiver_account_id=account.id,
                amount=interest,
                transaction_type="INTEREST",
                status="SUCCESS",
                description=f"Interest applied at rate {settings.INTEREST_APPLY_RATE}%"
            )
            db.add(txn)
        await db.commit()

@celery_app.task(name="calculate_interest")
def calculate_interest_task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_calculate_interest())
    return {"status": "completed"}