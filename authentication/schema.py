from ninja import Schema, ModelSchema
from django.conf import settings
from authentication.models import CustomUser
from typing import Optional

class UserIn(ModelSchema):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'type', 'password', 'country', 'phone']

class LoginIn(Schema):
    email: str
    password: str

class AuthOut(Schema):
    success: bool
    token: str
    email_verified: Optional[bool] = None
    email: Optional[str] = None

class ErrorOut(Schema):
    success: bool
    msg: str
    
class EmailExistOut(Schema):
    exist: bool