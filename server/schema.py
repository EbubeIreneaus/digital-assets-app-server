from decimal import Decimal
from ninja import Schema

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
    