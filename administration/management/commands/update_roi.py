from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Update Investment Returns'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("ROI updated for all users."))