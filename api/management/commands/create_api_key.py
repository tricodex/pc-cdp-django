"""
Management command to create API keys
"""
import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import APIKey

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a new API key for a user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user')
        parser.add_argument('--name', type=str, help='Name for the API key')
        parser.add_argument('--permissions', type=str, nargs='+', help='List of permissions')

    def handle(self, *args, **options):
        try:
            user = User.objects.get(email=options['email'])
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {options["email"]} does not exist')
            )
            return

        # Generate API key
        key = f"pa_{secrets.token_urlsafe(32)}"
        name = options.get('name', f"API Key for {user.email}")
        permissions = options.get('permissions', [])

        # Create API key
        api_key = APIKey.objects.create(
            user=user,
            name=name,
            key=key,
            permissions=permissions
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created API key'))
        self.stdout.write('Key: ' + self.style.WARNING(key))
        self.stdout.write('Please save this key as it won\'t be shown again')
        self.stdout.write('Key ID: ' + self.style.SUCCESS(str(api_key.id)))
