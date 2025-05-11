from django.contrib import admin
from .models import Transaction

# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    class Meta:
        fields = ['name']
        
admin.site.register(Transaction, TransactionAdmin)