from ninja import Schema, ModelSchema
from django.conf import settings
from authentication.models import CustomUser, NextOfKin, UserVerification, IdVerification
from typing import Optional

class Tier2Schema(ModelSchema):
    class Meta:
        model = UserVerification
        fields = ['status']

class Tier3Schema(ModelSchema):
    class Meta:
        model = IdVerification
        fields = ['status']

class UserIn(Schema):
    fullname: str
    email: str
    type: str
    password: str
    country: str
    phone: str
    referred_by: Optional[str] = None
        
class UserOut(ModelSchema):
    success: bool
    tier2: Optional[Tier2Schema] = None
    tier3: Optional[Tier3Schema] = None
    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'type', 'email_verified', 'country', 'phone', 'document_verified', 'profile_pics', 'tier', 'can_verify']
        
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

class ChangePasswordIn(Schema):
    current: str
    new: str
    confirm: str

class NextOfKinSchema(ModelSchema):
    class Meta:
        model = NextOfKin
        fields = ['fullname', 'email', 'phone', 'relationship', 'address', 'country']

class NextOfKinSchemaOut(Schema):
    success: bool
    data: Optional[NextOfKinSchema] = None
