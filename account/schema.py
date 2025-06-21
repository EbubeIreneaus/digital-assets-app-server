from ninja import Schema

from typing import Literal



    
class TransferBodyIn(Schema):
    amount: int
    source: Literal['balance', 'available_balance']
    to: str