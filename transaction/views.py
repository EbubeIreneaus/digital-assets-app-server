
import os
from django.utils import timezone
import random
import string
from django.conf import settings
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from administration.models import CryptoChannel
from authentication.models import CustomUser
from .models import Transaction

# Create your views here.

def formatDate(date):
    local_dt = timezone.localtime(date)
    return local_dt.strftime("%B %d, %Y – %I:%M %p")


def sendDepositEmail(depositId: int):
 
    try:
        deposit = Transaction.objects.get(id=depositId)
        channel = CryptoChannel.objects.get(name=deposit.channel)
        
        msg = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Deposit Received – Awaiting Confirmation</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: auto;
      background-color: #ffffff;
      border: 1px solid #ddd;
      padding: 20px;
      color: #1D3B53;
    }}
    .header {{
      text-align: center;
      padding-bottom: 20px;
    }}
    .header h2 {{
      margin: 0;
      color: #1D3B53;
    }}
    .transaction-details {{
      margin-bottom: 30px;
    }}
    .transaction-details table {{
      width: 100%;
      border-collapse: collapse;
    }}
    .transaction-details td {{
      padding: 8px 0;
    }}
    .label {{
      font-weight: bold;
      color: #1D3B53;
    }}
    .wallet-section {{
      text-align: center;
      margin: 30px 0;
    }}
    .wallet-address {{
      font-weight: bold;
      word-break: break-all;
      background: #f0f0f0;
      padding: 10px;
      display: inline-block;
      border-radius: 4px;
      margin-top: 10px;
      color: #1D3B53;
    }}
    .footer {{
      font-size: 14px;
      text-align: center;
      color: #666;
      margin-top: 30px;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h2>Deposit Received – Awaiting Confirmation</h2>
    </div>

    <div class="transaction-details">
      <table>
        <tr>
          <td class="label">Date & Time:</td>
          <td>{formatDate(deposit.createdAt)}</td>
        </tr>
        <tr>
          <td class="label">Amount:</td>
          <td>${deposit.amount}</td>
        </tr>
        <tr>
          <td class="label">Channel:</td>
          <td>Crypto Wallet ({deposit.channel.upper()})</td>
        </tr>
      </table>
    </div>

    <div class="wallet-section">
      <p><strong>Scan QR Code to Make Payment:</strong></p>
      <img src="{os.getenv('SERVER_URL')}/media/{channel.qrcode_image}" alt="QR Code" width="180" height="180">
      <p class="wallet-address">TX3u9xRkL6D7tMwPnR81Bq9EajGZ27E9hf</p>
    </div>

    <div class="footer">
      <p>Please reply to this email with a screenshot of your transaction once you have completed the payment.</p>
      <p>This deposit has been received but is still awaiting confirmation.</p>
    </div>
  </div>
</body>
</html>"""

        try:
            to = [deposit.user.email, settings.DEFAULT_FROM_EMAIL]
            subject = 'Deposit Received – Awaiting Confirmation'
            body = f""
           
            send_mail(
                recipient_list=to,
                html_message=msg,
                fail_silently=False,
                subject=subject,
                from_email=f'Digital Assets<{settings.DEFAULT_FROM_EMAIL}>',
                message=body
            )
           
        except Exception as error:
            print('verification email failed: '+ str(error))

    except Exception as error:
         print('verification email failed on end: '+ str(error))

def sendCreditAlert(instance):
    msg = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Credit Alert – Deposit Successful</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: 20px auto;
      background-color: #ffffff;
      border: 1px solid #ddd;
      padding: 20px;
      color: #1D3B53;
    }}
    .header {{
      text-align: center;
      padding-bottom: 20px;
    }}
    .header h2 {{
      margin: 0;
      color: #388E3C;
    }}
    .alert-box {{
      background-color: #e8f5e9;
      border-left: 6px solid #388E3C;
      padding: 16px;
      margin-bottom: 30px;
    }}
    .details-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    .details-table td {{
      padding: 8px 0;
    }}
    .label {{
      font-weight: bold;
      color: #1D3B53;
    }}
    .footer {{
      font-size: 14px;
      text-align: center;
      color: #777;
      margin-top: 30px;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h2>Credit Alert</h2>
      <p style="color: #555;">A deposit has been successfully credited to your account.</p>
    </div>

    <div class="alert-box">
      <p><strong>${instance.amount:.2f}</strong> has been credited to your account.</p>
    </div>

    <table class="details-table">
      <tr>
        <td class="label">Transaction Type:</td>
        <td>Deposit</td>
      </tr>
      <tr>
        <td class="label">Date & Time:</td>
        <td>{formatDate(instance.createdAt)}</td>
      </tr>
      <tr>
        <td class="label">Deposit Channel:</td>
        <td>Crypto Wallet ({instance.channel})</td>
      </tr>
      <tr>
        <td class="label">Desc:</td>
        <td>{instance.label}</td>
      </tr>
      <tr>
        <td class="label">Transaction Status:</td>
        <td><strong style="color: green;">Successful</strong></td>
      </tr>
    </table>

    <div class="footer">
      <p>If you have any questions about this transaction, feel free to contact our support team.</p>
      <p>Thank you for choosing our service.</p>
    </div>
  </div>
</body>
</html>
"""
    try:
      to = [instance.user.email, settings.DEFAULT_FROM_EMAIL]
      subject = "Credit Alert – Deposit Confirmed"
      send_mail(
        recipient_list=to,
        html_message=msg,
        fail_silently=False,
        message=msg,
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL
      )
      print('email sent successfully')
    except Exception as error:
      print('Error sending credit alert email ',str(error))

def sendWithdrawalEmail(withdrawId: int):
    try:
        withdraw = Transaction.objects.get(id=withdrawId)

        msg = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Withdrawal Request Received – Processing</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: auto;
      background-color: #ffffff;
      border: 1px solid #ddd;
      padding: 20px;
      color: #1D3B53;
    }}
    .header {{
      text-align: center;
      padding-bottom: 20px;
    }}
    .header h2 {{
      margin: 0;
      color: #1D3B53;
    }}
    .transaction-details {{
      margin-bottom: 30px;
    }}
    .transaction-details table {{
      width: 100%;
      border-collapse: collapse;
    }}
    .transaction-details td {{
      padding: 8px 0;
    }}
    .label {{
      font-weight: bold;
      color: #1D3B53;
    }}
    .footer {{
      font-size: 14px;
      text-align: center;
      color: #666;
      margin-top: 30px;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h2>Withdrawal Request Received – Processing</h2>
    </div>

    <div class="transaction-details">
      <table>
        <tr>
          <td class="label">ID:</td>
          <td>#TRW-{withdraw.id}</td>
        </tr>
        <tr>
          <td class="label">Fullname:</td>
          <td>{withdraw.user.fullname}</td>
        </tr>
        <tr>
          <td class="label">Date & Time:</td>
          <td>{formatDate(withdraw.createdAt)}</td>
        </tr>
        <tr>
          <td class="label">Amount:</td>
          <td>${withdraw.amount:.2f}</td>
        </tr>
        <tr>
          <td class="label">Withdrawal Channel:</td>
          <td>{withdraw.channel.upper()}</td>
        </tr>
        <tr>
          <td class="label">Wallet Address:</td>
          <td>{withdraw.wallet_address}</td>
        </tr>
      </table>
    </div>

    <div class="footer">
      <p>We have received your withdrawal request and it is currently being processed by our finance team.</p>
      <p>Processing time may vary depending on the payment network and verification requirements.</p>
      <p>You will receive another email once your withdrawal is confirmed and completed.</p>
    </div>
  </div>
</body>
</html>"""

        try:
            to = [withdraw.user.email]
            subject = 'Withdrawal Request Received – Processing'
            body = f""

            mail = EmailMultiAlternatives()
            mail.to = to
            mail.body = msg
            mail.attach_alternative(msg, 'text/html')
            mail.bcc = [settings.DEFAULT_FROM_EMAIL]
            mail.subject=subject
            mail.from_email=f'Digital Assets<{settings.DEFAULT_FROM_EMAIL}>'
            mail.send(fail_silently=False)
        
        except Exception as error:
            print('withdrawal email failed: ' + str(error))

    except Exception as error:
        print('withdrawal email failed on end: ' + str(error))
  
      
def sendDebitAlert(instance):
    msg = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Debit Alert – Withdrawal Successful</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f9f9f9;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: 20px auto;
      background-color: #ffffff;
      border: 1px solid #ddd;
      padding: 20px;
      color: #1D3B53;
    }}
    .header {{
      text-align: center;
      padding-bottom: 20px;
    }}
    .header h2 {{
      margin: 0;
      color: #D32F2F;
    }}
    .alert-box {{
      background-color: #fff3f3;
      border-left: 6px solid #D32F2F;
      padding: 16px;
      margin-bottom: 30px;
    }}
    .details-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }}
    .details-table td {{
      padding: 8px 0;
    }}
    .label {{
      font-weight: bold;
      color: #1D3B53;
    }}
    .footer {{
      font-size: 14px;
      text-align: center;
      color: #777;
      margin-top: 30px;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h2>Debit Alert</h2>
      <p style="color: #555;">A withdrawal has been successfully processed from your account.</p>
    </div>

    <div class="alert-box">
      <p><strong>${instance.amount:.2f}</strong> has been debited from your account.</p>
    </div>

    <table class="details-table">
      <tr>
        <td class="label">Transaction Type:</td>
        <td>Withdrawal</td>
      </tr>
      <tr>
        <td class="label">Date & Time:</td>
        <td>{format(instance.createdAt)}</td>
      </tr>
      <tr>
        <td class="label">Withdrawal Channel:</td>
        <td>Crypto Wallet ({instance.channel} - {instance.network})</td>
      </tr>
      <tr>
        <td class="label">Wallet Address:</td>
        <td>{instance.wallet_address}</td>
      </tr>
      <tr>
        <td class="label">Transaction Status:</td>
        <td><strong style="color: green;">Successful</strong></td>
      </tr>
    </table>

    <div class="footer">
      <p>If you did not initiate this transaction, please contact our support team immediately.</p>
      <p>Thank you for using our service.</p>
    </div>
  </div>
</body>
</html>
"""
    try:
      to = [instance.user.email, settings.DEFAULT_FROM_EMAIL]
      subject = "Credit Alert – Deposit Confirmed"
      send_mail(
        recipient_list=to,
        html_message=msg,
        fail_silently=False,
        message=msg,
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL
      )
      print('email sent successfully')
    except Exception as error:
      print('Error sending debit email ',str(error))
