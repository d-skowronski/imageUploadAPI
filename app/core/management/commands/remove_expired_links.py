'''
Django command to remove expired ExpiringLink objects
'''
from django.core.management.base import BaseCommand
from django.utils import timezone
from image_api.models import ExpiringLink


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Removing expired links to images...')
        to_delete = ExpiringLink.objects.filter(expiration__lte=(timezone.now()))
        # Removal happens through _raw_delete for better performance
        removed_count = to_delete._raw_delete(to_delete.db)

        self.stdout.write(self.style.SUCCESS(f'Removed {removed_count} expired links'))
