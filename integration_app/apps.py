from django.apps import AppConfig


class IntegrationAppConfig(AppConfig):
    name = "integration_app"

    def ready(self):
        from .toml import toml
        from .rails import MyRailsIntegration
        from .sep31 import MySEP31ReceiverIntegration
        from polaris.integrations import register_integrations
        register_integrations(
            toml=toml,
            rails=MyRailsIntegration(),
            sep31_receiver=MySEP31ReceiverIntegration(),
        )
