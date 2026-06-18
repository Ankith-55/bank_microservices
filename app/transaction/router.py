from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.transaction.schemas import DepositRequest, TransferRequest, TransactionResponse, TransactionDetail
from app.transaction.service import TransactionService
from app.core.dependencies import get_db, get_current_user
from app.account.service import AccountService
from app.models.user import User
import uuid

router = APIRouter()

@router.post("/deposit")
async def deposit(
    data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    acct_service = AccountService(db)
    account = await acct_service.get_my_account(current_user.id)
    service = TransactionService(db)
    return await service.deposit(account, data.amount)

@router.post("/transfer")
async def transfer(
    data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    acct_service = AccountService(db)
    sender_account = await acct_service.get_my_account(current_user.id)
    service = TransactionService(db)
    return await service.transfer(sender_account, data.receiver_account_number, data.amount)

@router.get("/history", response_model=list[TransactionResponse])
async def history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    acct_service = AccountService(db)
    account = await acct_service.get_my_account(current_user.id)
    service = TransactionService(db)
    txns = await service.get_transaction_history(account.id)
    return [
        {
            "transaction_id": str(t.id),
            "type": t.transaction_type,
            "amount": t.amount,
            "status": t.status,
            "created_at": t.created_at.isoformat()
        }
        for t in txns
    ]

@router.get("/{transaction_id}", response_model=TransactionDetail)
async def transaction_detail(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    acct_service = AccountService(db)
    account = await acct_service.get_my_account(current_user.id)
    service = TransactionService(db)
    txn = await service.get_transaction_detail(transaction_id, account.id)
    return {
        "transaction_id": str(txn.id),
        "sender_account_id": str(txn.sender_account_id) if txn.sender_account_id else None,
        "receiver_account_id": str(txn.receiver_account_id) if txn.receiver_account_id else None,
        "amount": txn.amount,
        "transaction_type": txn.transaction_type,
        "status": txn.status,
        "description": txn.description,
        "created_at": txn.created_at.isoformat()
    }