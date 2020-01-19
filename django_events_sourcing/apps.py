from django.apps import AppConfig


class DjangoEventsSourcingConfig(AppConfig):
    name = 'django_events_sourcing'

    def ready(self):
        from django_events_sourcing.register import register_models
        register_models()
