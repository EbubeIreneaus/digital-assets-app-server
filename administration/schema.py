from typing import List
from ninja import ModelSchema, Schema
from .models import CryptoChannel

class ChannelSchema(ModelSchema):
    class Meta:
        model = CryptoChannel
        fields = ['id', 'name', 'network']
        
class ChannelSchemaOut(Schema):
    success: bool
    data: List[ChannelSchema]
