import os

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create admin user and default domain site"

    def handle(self, *args, **kwargs):
        domain = os.getenv('DOMAIN')
        Site.objects.filter(id=1).update(domain=domain)

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('A super user already exists')
            return

        user = User(
            email=os.getenv('ADMIN_EMAIL'),
            username=os.getenv('ADMIN_USERNAME'),
            first_name=os.getenv('ADMIN_FIRST_NAME'),
            last_name=os.getenv('ADMIN_LAST_NAME'),
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        user.set_password(os.getenv('ADMIN_PASSWORD'))
        user.save()
        self.stdout.write(self.style.SUCCESS('Super user created'))
