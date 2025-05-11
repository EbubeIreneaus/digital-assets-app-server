from django.contrib import admin
from .models import CryptoChannel

# Register your models here.
class ChannelAdmin(admin.ModelAdmin):
    class Meta:
        fields = ['name']
        
admin.site.register(CryptoChannel, ChannelAdmin)
