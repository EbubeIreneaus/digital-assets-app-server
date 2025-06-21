from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.core.mail import send_mail
from .signals import send_tier2_approved_email, send_tier2_rejection_email, send_tier3_approved_email, send_tier3_rejected_email

class CustomUserManager(BaseUserManager):
    def create_user(self, email, fullname, phone, country, type='personal', password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            fullname=fullname,
            phone=phone,
            country=country,
            type=type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, fullname, phone, country, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, fullname, phone, country, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    TYPES = (
        ('personal', 'Personal'),
    )
    
    fullname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=18)
    country = models.CharField(max_length=40)
    type = models.CharField(max_length=20, choices=TYPES)
    email_verified = models.BooleanField(default=False)
    document_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_timestamp = models.DateTimeField(null=True, blank=True)
    profile_pics = models.ImageField(upload_to='profile/', blank=True, null=True)
    tier = models.IntegerField(default=1)
    can_verify = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'phone', 'country']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class IdVerification(models.Model):
    ID_TYPE_CHOICES=(
        ('passport', 'Passport'),
        ('licence', 'Driving Licence'),
        ('card', 'Government Issued Card'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="tier3")
    id_type = models.CharField(max_length=30, choices=ID_TYPE_CHOICES)
    image = models.ImageField(upload_to='verifications/ID/')
    createdAt = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending', choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')))

    
class UserVerification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="tier2")
    country_of_residence = models.CharField(max_length=200)
    firstname= models.CharField(max_length=50)
    middlename= models.CharField(max_length=50)
    lastname= models.CharField(max_length=50)
    dob = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=200)
    postal = models.CharField(max_length=10)
    city = models.CharField(max_length=20)
    selfie = models.ImageField(upload_to='verifications/people')
    status = models.CharField(max_length=20, default='pending', choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')))

class NextOfKin(models.Model):
    RELATIONSHIP_CHOICES = (
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('sibling', 'Sibling'),
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='nextofkin')
    fullname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=13)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=50)
    createdAt = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=CustomUser)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        msg = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Welcome to Digital Assets</title>
  <style>
    body {{
      font-family: 'Arial', sans-serif;
      background-color: #f4f6f8;
      margin: 0;
      padding: 0;
    }}
    .email-container {{
      max-width: 600px;
      margin: 30px auto;
      background-color: #ffffff;
      border: 1px solid #ddd;
      padding: 30px;
      color: #1D3B53;
    }}
    .header {{
      text-align: center;
      padding-bottom: 20px;
    }}
    .header h1 {{
      margin: 0;
      font-size: 28px;
      color: #1D3B53;
    }}
    .greeting {{
      margin-top: 20px;
      font-size: 16px;
      line-height: 1.6;
    }}
    .cta-button {{
      display: inline-block;
      margin: 30px 0;
      padding: 12px 24px;
      background-color: #1D3B53;
      color: #fff;
      text-decoration: none;
      border-radius: 5px;
      font-weight: bold;
    }}
    .features {{
      background-color: #f0f3f7;
      padding: 15px;
      margin-top: 20px;
      border-left: 4px solid #1D3B53;
    }}
    .footer {{
      font-size: 13px;
      text-align: center;
      color: #777;
      margin-top: 30px;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>Welcome to Digital Assets 🎉</h1>
    </div>

    <div class="greeting">
      <p>Hello <strong>{instance.fullname.title()}</strong>,</p>
      <p>We’re thrilled to have you on board! Your account has been successfully created, and you're now part of our growing community.</p>

      <p>With your account, you can:</p>
      <div class="features">
        <ul>
          <li>Make secure deposits & withdrawals</li>
          <li>Track your transactions in real-time</li>
          <li>Access investment options and financial tools</li>
        </ul>
      </div>

      <p>Ready to get started?</p>
      <a href="{{ login_url }}" class="cta-button">Log in to Your Dashboard</a>
    </div>

    <div class="footer">
      <p>If you have any questions or need help, feel free to reply to this email or contact support.</p>
      <p>– The Digital Assets Team</p>
    </div>
  </div>
</body>
</html>
"""
        to = [instance.email, settings.DEFAULT_FROM_EMAIL]
        from_email = f"Digital Assets<{settings.DEFAULT_FROM_EMAIL}>"
        try:
            send_mail(
            subject="Welcome to Digital Assets",
            message=msg,
            from_email=from_email,
            recipient_list=to,
            html_message=msg
            )
        except Exception as e:
            print('error sending welcome email', str(e))
            
@receiver(pre_save, sender=UserVerification)
def pre_save_user_verification(sender, instance, **kwargs):
    try:
        if instance.pk:  
            previous = UserVerification.objects.get(pk=instance.pk)
            if previous.status != instance.status:
                if instance.status == 'approved':
                    send_tier2_approved_email(instance)
                elif instance.status == 'rejected':
                    send_tier2_rejection_email(instance)
    except UserVerification.DoesNotExist:
        # This is a new record, no previous status to compare
        pass
    except Exception as e:
        print(f"[Signal Error] pre_save_user_verification: {e}")

@receiver(pre_save, sender=IdVerification)
def pre_save_id_verification(sender, instance, **kwargs):
    try:
        previous = IdVerification.objects.get(pk=instance.pk)
        if previous.status != instance.status:
            if instance.status == 'approved':
                send_tier3_approved_email(instance.user)
            elif instance.status == 'rejected':
                send_tier3_rejected_email(instance.user)
    except IdVerification.DoesNotExist:
        # This is a new record, no previous status to compare
        pass
    except Exception as e:
        print(f"[Signal Error] pre_save_id_verification: {e}")

