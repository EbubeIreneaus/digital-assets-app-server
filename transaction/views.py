
import os
from django.utils import timezone
import random
import string
from django.conf import settings
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives, send_mail

from administration.models import CryptoChannel
from authentication.models import CustomUser
from transaction.models import Transaction

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
            to = [deposit.user.email, 'service@digitalassets.com.ng']
            subject = 'Deposit Received – Awaiting Confirmation'
            body = f""
           
            send_mail(
                recipient_list=to,
                html_message=msg,
                fail_silently=False,
                subject=subject,
                from_email='Digital Assets<service@digitalassets.com.ng>',
                message=body
            )
            print('verification email send')
        except Exception as error:
            print('verification email failed: '+ str(error))

    except Exception as error:
         print('verification email failed on end: '+ str(error))
