from decimal import Decimal
from ninja import Schema, ModelSchema
from administration.models import InvestmentPlan
from transaction.models import Transaction
from account.models import Account
from typing import List, Literal

class ErrorOut(Schema):
    success: bool
    msg: str

class InvestPlanSchema(ModelSchema):
    class Meta:
        model = InvestmentPlan
        fields = ['name', 'label', 'icon', 'roi']

class TransactionSchema(ModelSchema):
    class Meta:
        model = Transaction
        fields = ['amount', 'label', 'createdAt', 'type','id']
        
class AccountSchema(ModelSchema):
    class Meta:
        model = Account
        fields = ['total_invested', 'total_gain']

class TradingPlanOutSchema(Schema):
    success: bool
    account: AccountSchema
    plans: List[InvestPlanSchema]
    
class MyPlanOut(Schema):
    success: bool = True
    plan: InvestPlanSchema
    balance: Decimal
    transactions: List[TransactionSchema]

class GetPlansOut(Schema):
    success:bool
    plans: List[InvestPlanSchema]
    
class BuyPlanIn(Schema):
    planName: str
    amount: int

class SellPlanIn(Schema):
    plan: str
    amount: int
    to: Literal['balance', 'available_balance']

class SwapPlanIn(Schema):
    source: str
    amount: int
    destination: str