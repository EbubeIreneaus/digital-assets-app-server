from django.conf import settings
from django.core.mail import send_mail

def send_tier2_approved_email(instance):
    try:
      msg = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Tier 2 Verification Approved</title>
  <style>
    body {{
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: 40px auto;
      background-color: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    .header {{
      background-color: #007BFF;
      color: white;
      padding: 20px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
    }}
    .content {{
      padding: 30px;
    }}
    .content h2 {{
      color: #333;
      font-size: 20px;
    }}
    .content p {{
      font-size: 16px;
      line-height: 1.6;
      color: #555;
    }}
    .footer {{
      text-align: center;
      padding: 20px;
      font-size: 13px;
      color: #aaa;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>Tier 2 Verification Approved</h1>
    </div>
    <div class="content">
      <h2>Hello {instance.user.fullname.title()},</h2>
      <p>Congratulations! Your <strong>Tier 2 verification</strong> has been successfully <strong>approved</strong>.</p>
      <p>You now have access to enhanced features and higher limits available to Tier 2 verified users.</p>
      <p>We appreciate your commitment to keeping your account secure and compliant.</p>
      <p>If you have any questions or need further assistance, feel free to reply to this email or reach out to our support team.</p>
      <p>Thank you for being a valued part of our community!</p>
      <p>– The Support Team</p>
    </div>
    <div class="footer">
      &copy; 2025 Digital Assets. All rights reserved.
    </div>
  </div>
</body>
</html>
"""
      to = [instance.user.email]
      send_mail(
        recipient_list=to,
        subject="Tier2 Verification Approved",
        html_message=msg,
        message="Your Tier 2 verification has been approved. You can now access enhanced features and higher limits.",
        from_email=f"Digital Assets<{settings.DEFAULT_FROM_EMAIL}>",
        fail_silently=False
      )
    #   print('Tier 2 verification approved email sent to', to[0])
    except Exception as error:
      print('Failed to send Tier 2 verification approved email:', str(error))
  
def send_tier2_rejection_email(instance):
    try:
      msg = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Tier 2 Verification Rejected</title>
  <style>
    body {{
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: 40px auto;
      background-color: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    .header {{
      background-color: #dc3545;
      color: white;
      padding: 20px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
    }}
    .content {{
      padding: 30px;
    }}
    .content h2 {{
      color: #333;
      font-size: 20px;
    }}
    .content p {{
      font-size: 16px;
      line-height: 1.6;
      color: #555;
    }}
    .footer {{
      text-align: center;
      padding: 20px;
      font-size: 13px;
      color: #aaa;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>Tier 2 Verification Rejected</h1>
    </div>
    <div class="content">
      <h2>Hello {instance.user.fullname.title()},</h2>
      <p>We regret to inform you that your <strong>Tier 2 verification</strong> request has been <strong>rejected</strong>.</p>
      <p>This may be due to incomplete or incorrect information or documents provided during the verification process.</p>
      <p>Please review the requirements carefully and re-submit your documents for verification. If you believe this was a mistake or need more details, feel free to contact our support team.</p>
      <p>We are here to help you through the process and look forward to your successful verification in the near future.</p>
      <p>– The Support Team</p>
    </div>
    <div class="footer">
      &copy; 2025 Your Company Name. All rights reserved.
    </div>
  </div>
</body>
</html>
"""
      to = [instance.user.email]
      send_mail(
        recipient_list=to,
        subject="Tier2 Verification Rejected",
        html_message=msg,
        message="Your Tier 2 verification has been rejected. Please review the requirements and re-submit your documents.",
        from_email=f"Digital Assets<{settings.DEFAULT_FROM_EMAIL}>",
        fail_silently=False
      )
    #  print('Tier 2 verification rejected email sent to', to[0])
    except Exception as error:
      print('Failed to send Tier 2 verification rejected email:', str(error))

def send_tier3_approved_email(user):
    subject = "Tier 3 Verification Approved!"
    from_email = f"Digital Assets <{settings.DEFAULT_FROM_EMAIL}>"
    to = [user.email]

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; color: #333; }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background: #fff;
                padding: 30px;
                border-radius: 6px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            }}
            h1 {{ color: #1d3b53; }}
            .button {{
                display: inline-block;
                margin-top: 20px;
                background: #1d3b53;
                color: #fff;
                padding: 10px 18px;
                border-radius: 4px;
                text-decoration: none;
                font-weight: bold;
            }}
            .footer {{
                font-size: 13px;
                color: #999;
                margin-top: 30px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 Congratulations, {user.fullname.title()}!</h1>
            <p>Your Tier 3 ID verification has been <strong>approved</strong>.</p>
            <p>You now have full access to our platform with increased transaction limits and priority support.</p>
            
            <div class="footer">
                <p>Need help? Reply to this email or contact our support team.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_mail(
        subject,
        "Your Tier 3 verification has been approved.",
        from_email,
        to,
        html_message=html_message
    )
        # print('Tier 3 verification approved email sent to', to[0])
    except Exception as error:
        print('Failed to send Tier 3 verification approved email:', str(error))

def send_tier3_rejected_email(user, reason=None):
    subject = "Tier 3 Verification Not Approved"
    from_email = f"Digital Assets <{settings.DEFAULT_FROM_EMAIL}>"
    to = [user.email]
    reason = None
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #fefefe; color: #333; }}
            .container {{
                max-width: 600px;
                margin: 30px auto;
                background: #fff;
                padding: 30px;
                border-radius: 6px;
                border: 1px solid #eee;
            }}
            h1 {{ color: #cc0000; }}
            .button {{
                display: inline-block;
                margin-top: 20px;
                background: #1d3b53;
                color: #fff;
                padding: 10px 18px;
                border-radius: 4px;
                text-decoration: none;
                font-weight: bold;
            }}
            .footer {{
                font-size: 13px;
                color: #999;
                margin-top: 30px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Tier 3 Verification Rejected</h1>
            <p>Dear {user.fullname.title()},</p>
            <p>We regret to inform you that your Tier 3 verification could not be approved at this time.</p>
            <p>{reason if reason else "Please review your submitted documents and ensure they meet our requirements."}</p>
            <p>You may try again by re-uploading valid documents that meet our requirements.</p>
            <div class="footer">
                <p>If you have any questions or need assistance, please contact our support team.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        send_mail(
            subject,
            "Your Tier 3 verification was not approved.",
            from_email,
            to,
            html_message=html_message
        )
        # print('Tier 3 verification rejected email sent to', to[0])
    except Exception as error:
        print('Failed to send Tier 3 verification rejected email:', str(error))

