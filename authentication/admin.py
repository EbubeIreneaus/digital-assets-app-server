from django.contrib import admin
from .models import CustomUser

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    class Meta:
        fields ="__all__"
        
admin.site.register(CustomUser, UserAdmin)
