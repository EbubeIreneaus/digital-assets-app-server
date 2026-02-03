from django.db import models
from django.conf import settings
from administration.models import InvestmentPlan
from authentication.models import CustomUser

# Create your models here.

class Account(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    available_balance = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)
    active_investment = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    total_withdrawal = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    Total_earnings = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    last_deposit = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    last_withdraw = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    total_invested = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    total_gain = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    referral_bonus = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    bonus = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    date = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.user.email
    
class Returns(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='returns')
    amount = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)
    plan = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.label} - {self.user.fullname}"
