from django.db import models
from administration.models import InvestmentPlan
from authentication.models import CustomUser

# Create your models here.
class Investment(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    plan = models.ForeignKey(InvestmentPlan, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)
    next_roi_date = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.user.email} {self.plan.label}'