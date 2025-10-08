from ninja import Schema, ModelSchema
from typing import List, Literal, Optional
from .models import Transaction

import transaction

class ResOut(Schema):
    success: bool
    msg: Optional[str] = None
    id: Optional[int] = None

class ErrorResOut(Schema):
    success: bool
    msg: bool

class Channel(Schema):
    name: str
    wallet_address: str
    qrcode_image: str
    network: str
    id: int

class ChannelResOut(Schema):
    success: bool
    data: Channel


class DepositIn(Schema):
    amount: int
    channel: str

class WithdrawalIn(Schema):
    amount: int
    channel: str
    # network: str
    wallet_address: str

class ToBalanceIn(Schema):
    amount: int

class TransactionSchema(ModelSchema):
    class Meta:
        model = Transaction
        fields = ['type','label', 'createdAt', 'amount', 'status', 'id', 'channel']
        
class TransactionOut(Schema):
    success: bool
    transactions: List[TransactionSchema]

class SingleTransactionOut(Schema):
    success: bool
    transaction: TransactionSchema
    
class TransactionFilterIn(Schema):
    status : Optional[Literal['all', 'pending', 'successful', 'failed']] = 'all'
    category : Optional[Literal['all', 'deposit', 'withdrawal', 'realestate', 'stock', 'crypto', 'retirement']] = 'all'
    offset : Optional[int] = 0
    limit : Optional[int] = 100