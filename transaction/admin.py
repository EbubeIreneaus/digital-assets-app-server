from django.contrib import admin
from .models import Transaction, Swap

# Register your models here.
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'label', 'status')
    search_fields = ('user__email', 'user__fullname', 'channel')
    list_filter = ('type', 'status')
    ordering = ('-createdAt',)
    
        
admin.site.register(Transaction, TransactionAdmin)

class SwapAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'source', 'destination', 'status')
    search_fields = ('user__email', 'user__fullname', 'id')
    list_filter = ('source', 'destination', 'status')
    ordering = ('-createdAt',)
    
        
admin.site.register(Swap, SwapAdmin)
