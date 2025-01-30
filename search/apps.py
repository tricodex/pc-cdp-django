from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search'

    def ready(self):
        # Delay the import and initialization
        from django.conf import settings
        if not settings.DEBUG or (
            hasattr(settings, 'ELASTICSEARCH_DSL_AUTOSYNC') 
            and settings.ELASTICSEARCH_DSL_AUTOSYNC
        ):
            from .models import init_indices
            init_indices()