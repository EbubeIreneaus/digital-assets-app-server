from django.db import models

# Create your models here.
class CryptoChannel(models.Model):
    name = models.CharField(max_length=15, unique=True)
    wallet_address = models.CharField(max_length=70)
    qrcode_image = models.ImageField(upload_to='crypto')
