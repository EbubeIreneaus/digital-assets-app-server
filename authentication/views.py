
from django.utils import timezone
import random
import string
from django.conf import settings
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives, send_mail

from authentication.models import CustomUser

# Create your views here.


def sendVerificationEmail(email):
    OTP = ''.join(random.choice(string.digits) for _ in range(6))
 
    try:
        user = CustomUser.objects.get(email__iexact=email)
        user.otp_code = OTP
        user.otp_timestamp = timezone.now()
        
        msg = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Verification Code</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="padding: 40px 0;">
    <tr>
      <td align="center">
        <table width="100%" style="max-width: 500px; background-color: #ffffff; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
          <tr>
            <td align="center">
              <h2 style="color: #1D3B53; margin-bottom: 24px;">Dear {user.fullname.split(' ')[-1]},</h2>
              <p style="font-size: 16px; color: #333; margin-bottom: 24px;">
                Your one-time verification code is:
              </p>
              <!-- Verification Code Box -->
              <div style="display: flex; justify-content: center; gap: 12px; font-size: 32px; letter-spacing: 4px; font-weight: bold; margin-bottom: 24px;">
                <span style="padding: 12px 16px; border: 2px solid #1D3B53; border-radius: 6px; color: #1D3B53;">{OTP[0]}</span>
                <span style="padding: 12px 16px; border: 2px solid #1D3B53; border-radius: 6px; color: #1D3B53;">{OTP[1]}</span>
                <span style="padding: 12px 16px; border: 2px solid #1D3B53; border-radius: 6px; color: #1D3B53;">{OTP[2]}</span>
                <span style="padding: 12px 16px; border: 2px solid #1D3B53; border-radius: 6px; color: #1D3B53;">{OTP[3]}</span>
                <span style="padding: 12px 16px; border: 2px solid #1D3B53; border-radius: 6px; color: #1D3B53;">{OTP[4]}</span>
                <span style="padding: 12px 16px; border: 2px solid #1D3B53; border-radius: 6px; color: #1D3B53;">{OTP[5]}</span>
              </div>
              <p style="font-size: 14px; color: #555;">
                This code is valid for 24 hours.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    
        try:
            to = [email]
            subject = 'Email Verification'
            body = f"Dear user, your one-time verification code is {OTP}. It is valid for 24 hours."
           
            send_mail(
                recipient_list=to,
                html_message=msg,
                fail_silently=False,
                subject=subject,
                message=body,
                from_email='Digital Assets<service@digitalassetsweb.com>',
            )
            user.save()
            print('verification email sent to', to[0])
        except Exception as error:
            print('verification email failed: '+ str(error))

    except Exception as error:
         print('verification email failed on end: '+ str(error))

