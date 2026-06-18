import uuid
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field
from typing import Optional

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sender_account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="accounts.id")
    receiver_account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="accounts.id")
    amount: Decimal = Field(max_digits=15, decimal_places=2)
    transaction_type: str = Field(max_length=20)
    status: str = Field(max_length=20, default="PENDING")
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)