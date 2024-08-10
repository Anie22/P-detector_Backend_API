from typing import Any
from django.core.management.base import BaseCommand
from accounts.models import *

class Command(BaseCommand):
    help = 'Create user profile for existing users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(user=user)