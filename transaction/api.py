from ninja import File, Form, Router, UploadedFile
from django.db import transaction
from administration.models import CryptoChannel
from administration.schema import ChannelSchemaOut
from authentication.models import CustomUser
from authentication.schema import ErrorOut
from transaction.schema import ChannelResOut, DepositIn, ResOut
from transaction.views import sendDepositEmail
from .models import Transaction
from django.core.mail import EmailMultiAlternatives

router = Router()

@router.get('/channel/{name}', auth=None, response={200: ChannelResOut, 500: ErrorOut})
def get_crypto_channels(request, name: str):
    try:
        channels = CryptoChannel.objects.get(name=name)
        return 200, {'success': True, 'data': channels}
    except Exception as error:
        return 500,  {'success': False, 'msg': str(error)}

@router.post('/deposit', response={200: ResOut, 500: ResOut})
@transaction.atomic
def deposit(request, data: DepositIn):
    try:
        data = data.dict()
        user = CustomUser.objects.get(id=request.auth['user']['id'])
        deposit = Transaction.objects.create(**data, type='deposit', user=user)
        sendDepositEmail(deposit.pk)
        return 200, {'success': True, 'id': deposit.pk}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}


@router.post("/pay_slip", auth=None)
def pay_slip(
    request,
    transactId: str = Form(...),
    amount: str = Form(...),
    channel: str = Form(...),
    file: UploadedFile = File(...)
):
    try:
        message = (
            '<h4><font color="#000000" style=""><span style="font-family: Arial Black;">'
            '<b style="">Someone just sent you a payment slip:</b></span></font></h4>'
            f'<p><font color="#000000" face="Arial Black"><b>Id: </b><span>{transactId}</span></font></p>'
            f'<p><font color="#000000" face="Arial Black"><b>Amount:</b><span>{amount}</span></font></p>'
            f'<p><font color="#000000" face="Arial Black"><b>Channel:</b><span>{channel}</span></font></p>'
            '<p style="text-align: left;"><font color="#000000" face="Arial Black">'
            '<span style="font-family: Arial;">See payment slip below</span></font></p>'
        )

        email = EmailMultiAlternatives(
            subject="Payment Confirmation",
            body="Someone just sent a payment slip.",
            to=["okigweebube7@gmail.com", "service@digitalassets.com.ng"]
        )
        email.attach_alternative(message, 'text/html')
        email.attach(file.name, file.read(), file.content_type)
        email.send(fail_silently=False)

        return {'status': 'success'}

    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

