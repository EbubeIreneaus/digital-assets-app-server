from ninja import Schema

from typing import Literal

class SellPlanIn(Schema):
    plan: Literal['realestate', 'stock', 'crypto', 'retirement']
    amount: int
    to: Literal['balance', 'available_balance']

class SwapPlanIn(Schema):
    source: Literal['realestate', 'stock', 'crypto', 'retirement']
    amount: int
    destination: Literal['realestate', 'stock', 'crypto', 'retirement']
