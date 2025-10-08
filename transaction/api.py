from typing import Literal, Optional
from django.conf import settings
from django.forms import model_to_dict
from ninja import File, Form, Router, UploadedFile
from django.db import transaction
from django.db.models import Q
from account.models import Account
from administration.models import CryptoChannel
from administration.schema import ChannelSchemaOut
from authentication.models import CustomUser
from authentication.schema import ErrorOut
from transaction.schema import ChannelResOut, DepositIn, ResOut, SingleTransactionOut, ToBalanceIn, TransactionFilterIn, TransactionOut, WithdrawalIn
from transaction.views import sendDepositEmail, sendWithdrawalEmail
from .models import Transaction
from django.core.mail import EmailMultiAlternatives
from datetime import datetime

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
        t = Transaction.objects.create(**data, type='withdraw', status='pending', user=account.user, label=f"withdraw to {data['channel']}")
        sendWithdrawalEmail(t.id)
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

@router.post('/withdrawal/to-balance')
def transfer_to_available_balance(request, body: ToBalanceIn):
    user = request.auth['user']
    data =  body.dict()
    now= datetime.now()
    try:
        message =f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Withdrawal Request</title>
    <style>
      body{{ font-family: Arial, sans-serif; color: #111; margin: 0; padding: 20px; }}
      .container {{ max-width: 600px; margin: 0 auto; border: 1px solid #e6e6e6; padding: 20px; border-radius: 6px; }}
      .header {{ font-size: 18px; font-weight: 600; margin-bottom: 10px; }}
      .info {{ margin: 16px 0; }}
      .buttons {{ margin-top: 20px; }}
      .button {{ display: inline-block; padding: 10px 16px; text-decoration: none; border-radius: 4px; font-weight: 600; }}
      .approve {{ background-color: #2d9cdb; color: #fff; }}
      .reject {{ background-color: #f2f2f2; color: #333; border: 1px solid #ddd; }}
      .meta {{ color: #666; font-size: 13px; margin-top: 18px; }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">Withdrawal Request</div>

      <div>Hello Admin,</div>

      <div class="info">
        <p><strong>User:</strong> {user['fullname']}</p>
        <p><strong>Email:</strong>{user['email']}</p>
        <p><strong>Requested amount:</strong> ${data['amount']:.2f}</p>
      </div>

      <div>
        <p>Please update users balance and available balance respectively.</p>
      </div>

      <div class="meta">
        <p>Requested on: {now.strftime("%B %d, %Y - %I:%M %p")}</p>
      </div>

      <div style="margin-top:18px; font-size:13px; color:#999;">
        This is an automated message—do not reply to this email.
      </div>
    </div>
  </body>
</html>
"""
        mail = EmailMultiAlternatives()
        mail.subject = 'Balance to Available Balance Request'
        mail.attach_alternative(message, 'text/html')
        mail.body = message
        mail.to = ['service@digitalassetsweb.com']
        
        mail.send(fail_silently=False)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'msg': str(e)}
    