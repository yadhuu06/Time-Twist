from django.apps import AppConfig


class AdminconsoleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AdminConsole'
    
    
from django.apps import AppConfig

class AdminConsoleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AdminConsole'

    def ready(self):
        from django.template import engines
        engines['django'].engine.template_libraries['custom_filters'] = 'AdminConsole.templatetags.custom_filters'