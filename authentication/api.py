from datetime import timedelta
from django.utils import timezone
from django.forms import model_to_dict
from ninja import Router, Form, File, UploadedFile
from ninja.security import HttpBearer
from django.db import transaction
from account.models import Account
from authentication.views import sendVerificationEmail
from .schema import ChangePasswordIn, EmailExistOut, LoginIn, NextOfKinSchema, NextOfKinSchemaOut, UserIn, AuthOut, ErrorOut, UserOut
from ninja.responses import codes_4xx, codes_5xx
from django.contrib.auth import authenticate
from authentication.models import CustomUser, NextOfKin, UserVerification, IdVerification
from extras.jwt import JwtSign, JwtVerify
from django.forms import model_to_dict


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
    response.pop('profile_pics', None)
    return JwtSign(response)


router = Router()


@router.put('/', response={201: AuthOut, codes_4xx: ErrorOut, codes_5xx: ErrorOut})
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
            return 200, {'success': True, 'token': token, 'email_verified': response['email_verified'], 'email': response['email']}
        return 404, {'success': False, 'msg': 'user not found'}
    except Exception as error:
        print(error)
        return 500, {'success': False, 'msg': 'unknow server error, try again'}


@router.post('/update-image', auth=AuthBearer())
def update_image(request, file: UploadedFile = File(...)):
    try:
        userId = request.auth['user']['id']
        user = CustomUser.objects.get(id=userId)
        user.profile_pics = file
        user.save()
        return {'success': True}
    except Exception as error:
        return {'success': False}


@router.get('/email-already-exist/{email}', response={200: EmailExistOut, 500: ErrorOut})
def check_if_email_exist_on_db(request, email: str):
    try:
        user_exist = CustomUser.objects.filter(email__iexact=email).exists()
        return 200, {'exist': user_exist}
    except Exception as error:
        return 500, {'msg': str(error)}


@router.get('/send_otp_code/', auth=AuthBearer())
def send_otp_code(request):
    try:
        userId = request.auth['user']['id']
        user = CustomUser.objects.get(id=userId)
        sendVerificationEmail(user.email)
        return 200, {"success": True}
    except Exception as error:
        return 500, {"success": False}


@router.get('/sendOtpWithoutAuth/{email}')
def send_otp_code_without_authentication(request, email: str):
    try:
        sendVerificationEmail(email)
        return 200, {"success": True}
    except Exception as error:
        return 500, {"success": False}


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
        return 500, {'success': False, 'msg': str(error)}


@router.get('/verify-otp-no-auth/{otp}', response={200: AuthOut, codes_4xx: ErrorOut, codes_5xx: ErrorOut})
@transaction.atomic
def verify_otp_without_auth(request, otp: int, email: str):
    try:
        user = CustomUser.objects.get(email__iexact=email)

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
        user.save()
        new_token_user = model_to_dict(user)
        token = generateJwtResponseToken(new_token_user)
        return 200, {'success': True, 'token': token}
    except CustomUser.DoesNotExist:
        return 404, {'success': False, 'msg': 'user not found'}
    except Exception as error:
        print(str(error))
        return 500, {'success': False, 'msg': str(error)}


@router.get('personal-information', auth=AuthBearer(), response={200: UserOut, 500: ErrorOut})
def get_user_personal_information(request):
    try:
        userId = request.auth['user']['id']
        user = CustomUser.objects.select_related(
            'tier2').select_related('tier3').get(id=userId)

        return 200, {'success': True, 
                     **model_to_dict(user), 
                     'tier2': model_to_dict(getattr(user, 'tier2', None)) if hasattr(user, 'tier2') else None,
                     'tier3': model_to_dict(getattr(user, 'tier3', None)) if hasattr(user, 'tier3') else None
                     }
    except Exception as error:
        print(error)
        return 500, {'success': False, 'msg': 'server error'}


@router.post('update-personal-information', auth=AuthBearer())
def update_user_information(request, body: UserOut):
    try:
        userId = request.auth['user']['id']
        data = body.dict()
        user = CustomUser.objects.get(id=userId)
        user.fullname = data['fullname']
        user.phone = data['phone']
        user.country = data['country']
        user.save()
        return {'success': True}
    except Exception as error:
        return {'success': False, 'msg': 'server error'}


@router.post('reset-password', auth=AuthBearer())
def reset_password(request, body: ChangePasswordIn):
    try:
        data = body.dict()
        userId = request.auth['user']['id']

        if len(data['new']) < 6:
            return {'success': False, 'msg': 'password must be six (6) characters or long'}
        if data['new'] != data['confirm']:
            return {'success': False, 'msg': 'confirm password does not match new password'}
        user = CustomUser.objects.get(id=userId)
        user.set_password(data['new'])
        user.save()
        return {'success': True}
    except Exception as error:
        return {'success': False, 'msg': 'unknown server error'}


@router.post('change-password', auth=AuthBearer())
def change_password(request, body: ChangePasswordIn):
    try:
        data = body.dict()
        userId = request.auth['user']['id']

        if len(data['new']) < 6 or len(data['current']) < 6:
            return {'success': False, 'msg': 'password must be six (6) characters or long'}
        if data['new'] != data['confirm']:
            return {'success': False, 'msg': 'confirm password does not match new password'}
        user = CustomUser.objects.get(id=userId)
        if not user.check_password(data['current']):
            return {'success': False, 'msg': 'current password does not match'}
        user.set_password(data['new'])
        user.save()
        return {'success': True}
    except Exception as error:
        return {'success': False, 'msg': 'unknown server error'}


@router.delete('/', auth=AuthBearer())
def delete_account(request):
    try:
        userId = request.auth['user']['id']
        CustomUser.objects.delete(id=userId)
        return {'success': True}
    except Exception as error:
        return {'success': False}


@router.post('tier2/', auth=AuthBearer())
def tier2_verification(
    request,
    selfie: UploadedFile = File(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    middlename: str = Form(...),
    dob: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    postal: str = Form(...),
    country: str = Form(...),
):
    try:
        userId = request.auth['user']['id']
        user = CustomUser.objects.get(id=userId)
        if UserVerification.objects.filter(user__id=userId).exists():
            return {'success': False, 'msg': 'Existing verification details found, contact support'}
        UserVerification.objects.create(user=user, firstname=firstname, lastname=lastname,
                                        middlename=middlename, dob=dob, address=address, city=city, postal=postal, country_of_residence=country, selfie=selfie)
        return {'success': True}
    except Exception as error:
        print(error)
        return {'success': False, 'msg': 'unknown server error occurred'}


@router.post('tier3/', auth=AuthBearer())
def tier3_verification(
    request,
    image: UploadedFile = File(...),
    country: str = Form(...),
    id_type: str = Form(...),
):
    try:
        userId = request.auth['user']['id']
        user = CustomUser.objects.get(id=userId)
        if IdVerification.objects.filter(user__id=userId).exists():
            return {'success': False, 'msg': 'Existing verification details found, contact support'}
        IdVerification.objects.create(
            user=user, country=country, id_type=id_type, image=image)
        return {'success': True}
    except Exception as error:
        print(error)
        return {'success': False, 'msg': 'unknown server error occurred'}


@router.post('next-of-kin', auth=AuthBearer())
def add_next_of_kin(request, body: NextOfKinSchema):
    try:
        userId = request.auth['user']['id']
        if NextOfKin.objects.filter(user__id=userId).exists():
            return {'success': False, 'msg': 'Existing next of kin details found, contact support'}
        user = CustomUser.objects.get(id=userId)
        NextOfKin.objects.create(user=user, **body.dict())
        return {'success': True}
    except Exception as error:
        print(error)
        return {'success': False, 'msg': 'unknown server error occurred'}


@router.get('next-of-kin', auth=AuthBearer(), response={200: NextOfKinSchemaOut, 404: ErrorOut, 500: ErrorOut})
def get_next_of_kin(request):
    try:
        userId = request.auth['user']['id']
        next_of_kin = NextOfKin.objects.get(user__id=userId)
        return 200, {'success': True, 'data': next_of_kin}
    except NextOfKin.DoesNotExist:
        return 404, {'success': False, 'msg': 'No next of kin details found'}
    except Exception as error:
        print(error)
        return 500, {'success': False, 'msg': 'unknown server error occurred'}


@router.delete('next-of-kin', auth=AuthBearer())
def delete_next_of_kin(request):
    try:
        userId = request.auth['user']['id']
        next_of_kin = NextOfKin.objects.get(user__id=userId)
        next_of_kin.delete()
        return {'success': True}
    except NextOfKin.DoesNotExist:
        return {'success': False, 'msg': 'No next of kin details found'}
    except Exception as error:
        print(error)
        return {'success': False, 'msg': 'unknown server error occurred'}
