from ninja import Schema, ModelSchema
from typing import Optional

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

class ChannelResOut(Schema):
    success: bool
    data: Channel


class DepositIn(Schema):
    amount: int
    channel: str