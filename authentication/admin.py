from django.contrib import admin
from .models import CustomUser, IdVerification, NextOfKin, UserVerification
from account.models import Account
# Register your models here.

class AccountInline(admin.StackedInline):
    model = Account
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Account'
    extra = 0

class IdVerificationInline(admin.StackedInline):
    model = IdVerification
    fk_name = 'user'
    verbose_name_plural = 'Tier3 Verification'
    extra = 0

class UserVerificationInline(admin.StackedInline):
    model = UserVerification
    fk_name = 'user'
    verbose_name_plural = 'Tier2 Verification'
    extra = 0

class NextOfKinInline(admin.StackedInline):
    model = NextOfKin
    fk_name = 'user'
    verbose_name_plural = 'Next of Kin'
    extra = 0

class UserAdmin(admin.ModelAdmin):
    exclude = ['user_permissions', 'groups', 'last_login', 'password', 'is_superuser', 'is_staff']
    inlines= [AccountInline, UserVerificationInline, IdVerificationInline, NextOfKinInline]

        
admin.site.register(CustomUser, UserAdmin)

