from pydantic import BaseModel
from decimal import Decimal

class AccountCreateResponse(BaseModel):
    id: str
    user_id: str
    account_number: str
    balance: Decimal

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_number: str
    created_at: str
    updated_at: str

class BalanceResponse(BaseModel):
    account_number: str
    balance: Decimal