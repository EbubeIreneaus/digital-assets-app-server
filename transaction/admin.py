from django.contrib import admin
from .models import Transaction

# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'label', 'status')
    search_fields = ('user__email', 'user__fullname', 'channel')
    list_filter = ('type', 'status')
    ordering = ('-createdAt',)
    
        
admin.site.register(Transaction, TransactionAdmin)