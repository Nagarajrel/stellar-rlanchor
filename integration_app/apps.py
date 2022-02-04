from django.apps import AppConfig


class IntegrationAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integration_app'

    def ready(self):
        from polaris.integrations import register_integrations
        from .customers import MyCustomerIntegration
        from .rails import MyRailsIntegration
        from .sep31 import MySEP31ReceiverIntegration
        from .toml import toml
        register_integrations(
            toml=toml,
            rails=MyRailsIntegration(),
            sep31_receiver=MySEP31ReceiverIntegration(),
            customer=MyCustomerIntegration(),
        )
