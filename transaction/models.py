from django.db import models
from django.forms import model_to_dict
from administration.models import CryptoChannel, InvestmentPlan
from authentication.models import CustomUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from .signal import transaction_signal_handling, swap_handling
# Create your models here.

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('withdraw', 'Withdrawal'),
        ('deposit', 'Deposit'),
        ('realestate', 'Real Estate'),
        ('stock', 'Stock'),
        ('crypto', 'Cryptocurrency'),
        ('retirement', 'Retirement'),
    )
    
    STATUS_CHOICES = (
        ('successful', 'Successful'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, default=0.00, max_digits=8)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    createdAt =models.DateTimeField(auto_now_add=True)
    channel = models.CharField(max_length=255)
    network = models.CharField(max_length=255, blank=True, null=True)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f'{self.user.fullname} {self.channel}'

class Swap(models.Model):
    STATUS_CHOICES = (
        ('successful', 'Successful'),
        ('pending', 'Pending'),
        ("failed", "Failed")
    )

    WALLET_CHOICES = (
        ('balance', 'Balance'),
        ('available', 'Available Balance')
    )
    source = models.CharField(max_length=15, choices=WALLET_CHOICES)
    destination = models.CharField(max_length=15, choices=WALLET_CHOICES)
    amount = models.DecimalField(decimal_places=2, default=0.00, max_digits=8)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    createdAt =models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f'{self.user.fullname} {self.source} to {self.destination}'
    
@receiver(post_save, sender=Transaction)
def confirm_transaction_signal(sender, instance, created, **kwargs):
   
    if created:
        pass

    elif instance.status == 'successful' and (instance.type == 'deposit' or instance.type == 'withdraw'):
        
        transaction_signal_handling(instance)

@receiver(post_save, sender=Swap)
def action_for_swap(sender, instance, created, **kwargs):
    if created:
        pass
    else:
        swap_handling(instance)
        
