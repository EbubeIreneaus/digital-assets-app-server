from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

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
    phone = models.CharField(max_length=13)
    country = models.CharField(max_length=40)
    type = models.CharField(max_length=20, choices=TYPES)
    email_verified = models.BooleanField(default=False)
    document_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_timestamp = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'phone', 'country']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
