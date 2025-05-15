from django.contrib import admin
from .models import Investment

# Register your models here.
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'active']

admin.site.register(Investment, InvestmentAdmin)