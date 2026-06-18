import uuid
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from app.models.user import User

class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    account_number: str = Field(max_length=20, unique=True, index=True)
    balance: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship()