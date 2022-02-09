from django.apps import AppConfig


class IntegrationAppConfig(AppConfig):
    name = "integration"

    def ready(self):
        from .sep1.toml import toml
        from .sep24.rails import MyRailsIntegration
        from .sep31.sep31 import MySEP31ReceiverIntegration
        from polaris.integrations import register_integrations
        register_integrations(
            toml=toml,
            rails=MyRailsIntegration(),
            sep31_receiver=MySEP31ReceiverIntegration(),
        )
