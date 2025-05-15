from django.db import models

# Create your models here.
class CryptoChannel(models.Model):
    name = models.CharField(max_length=15, unique=True)
    wallet_address = models.CharField(max_length=70)
    qrcode_image = models.ImageField(upload_to='crypto')
    
    def __str__(self):
        return self.name


class InvestmentPlan(models.Model):
    name = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=30, unique=True, blank=True, null=True)
    roi = models.IntegerField()
    icon= models.ImageField(upload_to='icon')
    
    def __str__(self):
        return self.label