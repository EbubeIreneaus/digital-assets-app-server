from django.db import models
from administration.models import CryptoChannel
from authentication.models import CustomUser

# Create your models here.
class Transaction(models.Model):
    type = (
        ('withdraw', 'Withdrawal'),
        ('deposit', 'Deposit')
    )
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(decimal_places=2, default=0.00, max_digits=8)
    type = models.CharField(max_length=15, choices=type)
    createdAt =models.DateTimeField(auto_now_add=True)
    channel = models.CharField(max_length=15)
    wallet_address = models.CharField(max_length=70, blank=True, null=True)
    
    def __str__(self):
        return f'{self.user.fullname} {self.channel}'