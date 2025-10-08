from decimal import Decimal
from typing import List, Optional
from ninja import Schema, ModelSchema
from transaction.models import Transaction

class ErrorOut(Schema):
    success: bool
    msg: str
class ResOut(Schema):
    success: bool
    data: Optional[str | dict] = None
    
class UserSchema(Schema):
    fullname: str
    profile_pics: Optional[str] = None
    
class Accountschema(Schema):
    balance: Decimal
    available_balance: Decimal

class TransactionSchema(ModelSchema):
    class Meta:
        model = Transaction
        fields = ['type', 'label', 'amount', 'createdAt', 'id', 'status']

class DashboardDataSchema(Schema):
    success: bool
    user: UserSchema
    account: Accountschema
    liveChat: str
    transactions: List[TransactionSchema]


class RefMeSchema(Schema):
    referral_code: str

class RefereeSchema(Schema):
    id: int
    fullname: str
    has_first_deposit: bool

class ReferralSchema(Schema):
    success: bool
    me: RefMeSchema
    referee: List[RefereeSchema]
    
    