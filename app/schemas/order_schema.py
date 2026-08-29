import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateOrder(BaseModel):
    item_id: int
    quantity: int
    price: Decimal


class OrderEvent(CreateOrder):
    order_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "PENDING"
