from django.contrib import admin
from .models import CryptoChannel, InvestmentPlan, SupportChannel

# Register your models here.
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name']
        
admin.site.register(CryptoChannel, ChannelAdmin)

class InvestPlanAdmin(admin.ModelAdmin):
    list_display= ['label', 'roi']
    
admin.site.register(InvestmentPlan, InvestPlanAdmin)
admin.site.register(SupportChannel)
