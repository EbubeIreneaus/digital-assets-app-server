from django.contrib import admin
from .models import Account

# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    class Meta:
        field = '__all__'
        
admin.site.register(Account, AccountAdmin)
