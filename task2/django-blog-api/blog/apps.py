
from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = 'Blog API'

    def ready(self):
        """Import signal handlers when the app is ready"""
        import blog.signals
