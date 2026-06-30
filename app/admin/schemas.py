from pydantic import BaseModel
from decimal import Decimal

class UserAdminResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    is_active: bool

class AccountAdminResponse(BaseModel):
    account_number: str
    user_id: str
    balance: Decimal