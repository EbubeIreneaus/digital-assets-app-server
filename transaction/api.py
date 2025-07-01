from typing import Literal, Optional
from django.forms import model_to_dict
from ninja import File, Form, Router, UploadedFile
from django.db import transaction
from django.db.models import Q
from account.models import Account
from administration.models import CryptoChannel
from administration.schema import ChannelSchemaOut
from authentication.models import CustomUser
from authentication.schema import ErrorOut
from transaction.schema import ChannelResOut, DepositIn, ResOut, SingleTransactionOut, TransactionFilterIn, TransactionOut, WithdrawalIn
from transaction.views import sendDepositEmail
from .models import Transaction
from django.core.mail import EmailMultiAlternatives

router = Router()


@router.get('/channel/{id}', auth=None, response={200: ChannelResOut, 500: ErrorOut})
def get_crypto_channels(request, id: int):
    try:
        channels = CryptoChannel.objects.get(id=id)
        return 200, {'success': True, 'data': channels}
    except Exception as error:
        return 500,  {'success': False, 'msg': str(error)}


@router.post('/deposit', response={200: ResOut, 500: ResOut})
@transaction.atomic
def deposit(request, data: DepositIn):
    try:
        data = data.dict()
        channel = data['channel']
        user = CustomUser.objects.get(id=request.auth['user']['id'])
        deposit = Transaction.objects.create(**data, type='deposit', user=user, label=f"deposited into account - {data['channel']}")
        sendDepositEmail(deposit.pk)
        return 200, {'success': True, 'id': deposit.pk}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}
    
@router.post('/withdrawal')
def withdrawal(request, body: WithdrawalIn):
    try:
        userId= request.auth['user']['id']
        data = body.dict()
        account = Account.objects.get(user__id=userId)
        if account.available_balance < data['amount']:
            return {'success': False, 'msg': 'Insufficient Balance'}
        Transaction.objects.create(**data, type='withdraw', status='pending', user=account.user, label=f"withdraw to {data['channel']}")
        # send email
        return {'success': True}
    except Exception as error:
        return {'success': False, 'msg': 'unknown server error'}


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


@router.get('/all', response={200: TransactionOut, 500: ErrorOut})
def get_all_transactions(request, status: Optional[str] = 'all', category:Optional[str]= 'all', offset: Optional[int]=0, limit: Optional[int]=100):
    try:
        userId = request.auth['user']['id']
        query = Q(user__id=userId)

        if category != 'all':
            query &= Q(type__iexact=category)

        if status != 'all':
            query &= Q(status__iexact=status)

        transactions = Transaction.objects.filter(query).order_by('-id')[offset : limit]
        return 200, {'success': True, 'transactions': transactions}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}

@router.get('/one/{id}', response={200: SingleTransactionOut, 500: ErrorOut })
def get_one_transaction(request, id: int):
    try:
        userId = request.auth['user']['id']
        transaction = Transaction.objects.get(id=id)
        return 200,{'success': True, 'transaction':transaction}
    except Exception as error:
        return 500, {'success': False, 'msg': str(error)}

