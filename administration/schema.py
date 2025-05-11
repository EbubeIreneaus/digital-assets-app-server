from typing import List
from ninja import ModelSchema, Schema
from .models import CryptoChannel

class ChannelSchema(ModelSchema):
    class Meta:
        model = CryptoChannel
        fields = ['name']
        
class ChannelSchemaOut(Schema):
    success: bool
    data: List[ChannelSchema]