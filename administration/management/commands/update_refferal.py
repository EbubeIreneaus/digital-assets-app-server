from authentication.models import CustomUser
from django.core.management.base import BaseCommand
from authentication.api import generate_referral_code

class Command(BaseCommand):
    help = 'Update all users without ROI'

    def handle(self, *args, **options):
        try:
            users = CustomUser.objects.filter(referral_code__isnull=True)
            for user in users:
                user.referral_code = generate_referral_code(user.email)
                user.save(update_fields=['referral_code'])
                self.stdout.write(self.style.SUCCESS(f'Code - {user.referral_code} generated for {user.fullname}'))
            self.stdout.write(self.style.SUCCESS(f'code generated for all users'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during referral code execution {str(e)}'))
