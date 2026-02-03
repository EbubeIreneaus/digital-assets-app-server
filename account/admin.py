from django.contrib import admin
from .models import Account, Returns

# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    class Meta:
        field = '__all__'

class ReturnsAdmin(admin.ModelAdmin):
    class Meta:
        list_display = ['user', 'amount', 'label']
        
admin.site.register(Account, AccountAdmin)
admin.site.register(Returns, ReturnsAdmin)
