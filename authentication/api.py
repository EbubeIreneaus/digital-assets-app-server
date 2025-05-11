from datetime import timedelta
from django.utils import timezone
from django.forms import model_to_dict
from ninja import Router, Form
from ninja.security import HttpBearer
from django.db import transaction
from account.models import Account
from authentication.views import sendVerificationEmail
from .schema import EmailExistOut, LoginIn, UserIn, AuthOut, ErrorOut
from ninja.responses import codes_4xx, codes_5xx
from django.contrib.auth import authenticate
from authentication.models import CustomUser
from extras.jwt import JwtSign, JwtVerify

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if not token:
            return False
        return JwtVerify(token)
    
def generateJwtResponseToken(response: dict):
    response.pop('password', None)
    response.pop('otp_code', None)
    response.pop('otp_timestamp', None)
    response.pop('user_permissions', None)
    return JwtSign(response)

router = Router()


@router.put('/', response={201: AuthOut, codes_4xx: ErrorOut, codes_5xx:ErrorOut})
@transaction.atomic
def create(request, user: UserIn):
    try:
        user_dict = user.dict()
        user_model = CustomUser.objects.create_user(**user_dict)
        account = Account.objects.create(user=user_model)
        response = model_to_dict(user_model)
        token = generateJwtResponseToken(response)
        return 201, {'token': token, "success": True, 'email_verified': response['email_verified'], 'email': response['email']}
    except Exception as error:
        return 500, {'msg': str(error), 'success': False}


@router.post('/', response={200: AuthOut, codes_4xx: ErrorOut, codes_5xx: ErrorOut})
def login(request, user: LoginIn):
    try:
        user_dict = user.dict()
        user = authenticate(**user_dict)
        if user is not None:
            response = model_to_dict(user)
            token = generateJwtResponseToken(response)
            return 200, {'success':True, 'token': token, 'email_verified': response['email_verified'], 'email': response['email']}
        return 404, {'success': False, 'msg':'user not found'}
    except Exception as error:
        print(error)
        return 500, {'success': False, 'msg': 'unknow server error, try again'}
    
@router.get('/email-already-exist/{email}', response={200: EmailExistOut, 500: ErrorOut})
def check_if_email_exist_on_db(request, email: str):
    try:
        user_exist = CustomUser.objects.filter(email__iexact=email).exists()
        return 200, {'exist': user_exist}
    except Exception as error:
        return 500, {'msg': str(error)}
    
@router.get('/send_otp_code/{email}')
def send_otp_code(request, email: str):
    sendVerificationEmail(email)
    return 200, {"success": True}


@router.get('/verify-otp/{otp}', response={200: AuthOut, codes_4xx: ErrorOut, codes_5xx: ErrorOut}, auth=AuthBearer())
@transaction.atomic
def verify_otp(request, otp: int):
    try:
        user = CustomUser.objects.get(id=request.auth['user']['id'])

        if user.otp_code is None or user.otp_timestamp is None:
            return 400, {'success': False, 'msg': 'no saved OTP for user'}
        otp_expiry = user.otp_timestamp + timedelta(hours=24)
        now = timezone.now()
        if now > otp_expiry:
            return 400, {'success': False, 'msg': 'OTP time has expired'}
        print(otp)
        if int(user.otp_code) != otp:
            return 400, {'success': False, 'msg': 'OTP code is invalid'}
        
        # code is valid and within time 24 hours of request
        user.otp_code = None
        user.otp_timestamp = None
        user.email_verified = True
        user.save()
        new_token_user = model_to_dict(user)
        token = generateJwtResponseToken(new_token_user)
        return 200, {'success': True, 'token': token}
    except CustomUser.DoesNotExist:
        return 404, {'success': False, 'msg': 'user not found'}
    except Exception as error:
       print(str(error))
       return 500, {'success':False, 'msg': str(error)}