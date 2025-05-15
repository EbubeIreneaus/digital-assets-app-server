from decimal import Decimal
from typing import Optional
from ninja import Schema

class ErrorOut(Schema):
    success: bool
    msg: str
class ResOut(Schema):
    success: bool
    data: Optional[str | dict] = None
    
class UserSchema(Schema):
    fullname: str
    
class Accountschema(Schema):
    balance: Decimal
    available_balance: Decimal

class TransactionSchema(Schema):
    type: str
    amount: Decimal

class DashboardDataSchema(Schema):
    success: bool
    user: UserSchema
    account: Accountschema
    