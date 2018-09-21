from django.apps import AppConfig


class GrowsConfig(AppConfig):
    name = 'grows'

    def ready(self):
        # import grows.signals
        pass
