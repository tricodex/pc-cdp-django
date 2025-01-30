"""
Application configuration for agents app
"""
from django.apps import AppConfig


class AgentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agents'
    verbose_name = 'Agents'

    def ready(self):
        try:
            import agents.signals  # noqa
        except ImportError:
            pass