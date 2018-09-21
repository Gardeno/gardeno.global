from django.apps import AppConfig


class GrowsConfig(AppConfig):
    name = 'grows'

    def ready(self):
        print('Imported signals...')
        import grows.signals
