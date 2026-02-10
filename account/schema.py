from ninja import Schema

from typing import Literal, Optional


class TransferBodyIn(Schema):
    amount: int
    source: Literal['balance', 'available_balance']
    to: str
    password: Optional[str] = None
