from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from dateutil import parser


def formatDate(date):
    if isinstance(date, str):
        date = parser.parse(date)
    local_dt = timezone.localtime(date)
    return local_dt.strftime("%B %d, %Y – %I:%M %p")

# Create your views here.

def send_visa_email(instance):
    msg = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Visa Application Received</title>
  <style>
    body {{
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f5f7fa;
      color: #333;
      margin: 0;
      padding: 0;
    }}

    .container {{
      max-width: 600px;
      margin: 40px auto;
      background-color: #ffffff;
      padding: 40px 30px;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    }}

    .header {{
      text-align: center;
      padding-bottom: 20px;
    }}

    .header h1 {{
      color: #2c3e50;
      font-size: 24px;
      margin-bottom: 10px;
    }}

    .header p {{
      color: #777;
      font-size: 16px;
      margin: 0;
    }}

    .message {{
      margin-top: 30px;
      font-size: 16px;
      line-height: 1.6;
    }}

    .message strong {{
      color: #2c3e50;
    }}

    .footer {{
      margin-top: 40px;
      text-align: center;
      font-size: 14px;
      color: #999;
    }}

    .highlight {{
      color: #0077cc;
      font-weight: 600;
    }}

    .btn {{
      display: inline-block;
      margin-top: 25px;
      background-color: #0077cc;
      color: #fff;
      padding: 12px 24px;
      text-decoration: none;
      border-radius: 6px;
      font-weight: bold;
      transition: background 0.3s;
    }}
    .btn:hover {{
      background-color: #005fa3;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Visa Application Received</h1>
      <p>Thank you for choosing us!</p>
    </div>

    <div class="message">
      <p>Hello <strong>{instance.user.fullname.title()}</strong>,</p>

      <p>
        We have successfully received your visa application. Our team has started processing your request and one of our dedicated flight agents will get in touch with you as soon as possible to guide you through the next steps.
      </p>

      <p>
        In the meantime, feel free to reach out if you have any urgent questions or need to make changes to your application.
      </p>

      <a href="mailto:support@digitalassetsweb.com" class="btn">Contact Support</a>
    </div>

    <div class="footer">
      &copy; 2025 Your Travel Agency. All rights reserved.
    </div>
  </div>
</body>
</html>
"""
    to = [instance.user.email, settings.DEFAULT_FROM_EMAIL]
    subject = 'Visa Application Recieved'
    
    try:
        send_mail(
            recipient_list= to,
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject=subject,
            message=msg,
            html_message=msg,
            fail_silently=False
        )
        print('Email Sent, flight booking')
    except Exception as error:
        print('Failed to send flight booking email',  str(error))
    
def send_flight_email(instance):
    msg = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      margin: 0;
      padding: 0;
    }}
    .container {{
      background-color: #ffffff;
      max-width: 600px;
      margin: 40px auto;
      padding: 20px 30px;
      border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    h2 {{
      color: #2a9d8f;
    }}
    .details {{
      margin-top: 20px;
      line-height: 1.6;
    }}
    .footer {{
      margin-top: 30px;
      font-size: 13px;
      color: #888;
    }}
    .label {{
      font-weight: bold;
    }}
    @media (max-width: 600px) {{
      .container {{
        padding: 15px 20px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h2>Flight Booking Confirmation</h2>

    <p>Hello {instance.user.fullname},</p>

    <p>We’ve received your flight booking request. One of our agents will get back to you shortly to confirm the details and proceed with the next steps.</p>

    <div class="details">
      <p><span class="label">Trip Type:</span> {'Return' if instance.trip_type == 'return' else 'One Way' if instance.trip_type == 'oneway' else 'Multi City'} Trip</p>
      <p><span class="label">From:</span> {instance.from_city.title()}</p>
      <p><span class="label">To:</span> {instance.to_city.title()}</p>
      <p><span class="label">Departure Date:</span> {formatDate(instance.departure_date)}</p>
        <p><span class="label">Return Date:</span> {formatDate(instance.arrival_date) if instance.arrival_date else "Nill"}</p>
      <p><span class="label">No of Passengers</span> {instance.passenger}</p>
       <p><span class="label">Boarding Class</span> {instance.boarding_class.title()}</p>
    </div>

    <p>Thank you for choosing us.<br />— The Digital Assets FlightTeam</p>

    <div class="footer">
      <p>If you didn’t initiate this booking, please ignore this email or contact us.</p>
    </div>
  </div>
</body>
</html>
"""
    to = [instance.user.email, settings.DEFAULT_FROM_EMAIL]
    subject =  'Flight Booking - Digital Assets'
    try:
        send_mail(
            recipient_list= to,
            from_email=settings.DEFAULT_FROM_EMAIL,
            subject=subject,
            message=msg,
            html_message=msg,
            fail_silently=False
        )
        print('Email Sent, flight booking')
    except Exception as error:
        print('Failed to send flight booking email',  str(error))

