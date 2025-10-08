from django.db import models

# Create your models here.
class CryptoChannel(models.Model):
    name = models.CharField(max_length=15)
    wallet_address = models.CharField(max_length=70)
    network = models.CharField(max_length=50, null=True, blank=True)
    qrcode_image = models.ImageField(upload_to='crypto')
    
    def __str__(self):
        return self.name


class InvestmentPlan(models.Model):
    name = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=30, unique=True, blank=True, null=True)
    roi = models.FloatField()
    icon= models.ImageField(upload_to='icon')
    
    def __str__(self):
        return self.label
    
class SupportChannel(models.Model):
    phone = models.CharField(max_length=20)
    facebook_url = models.URLField()
    telegram_url = models.URLField()
    twitter_url = models.URLField()