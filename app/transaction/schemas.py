from pydantic import BaseModel, condecimal
from decimal import Decimal
from typing import Optional

class DepositRequest(BaseModel):
    amount: condecimal(gt=0, max_digits=15, decimal_places=2)

class TransferRequest(BaseModel):
    receiver_account_number: str
    amount: condecimal(gt=0, max_digits=15, decimal_places=2)

class TransactionResponse(BaseModel):
    transaction_id: str
    type: str
    amount: Decimal
    status: str
    created_at: str

class TransactionDetail(BaseModel):
    transaction_id: str
    sender_account_id: Optional[str]
    receiver_account_id: Optional[str]
    amount: Decimal
    transaction_type: str
    status: str
    description: Optional[str]
    created_at: str