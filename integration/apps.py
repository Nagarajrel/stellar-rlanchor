from django.apps import AppConfig


class IntegrationAppConfig(AppConfig):
    name = "integration"

    def ready(self):
        from .sep1.toml import toml
        from .sep24.rails import MyRailsIntegration
        from .sep24.deposit import MyDepositIntegration
        from .sep24.withdraw import MyWithdrawIntegration
        from .sep31.sep31 import MySEP31ReceiverIntegration
        from polaris.integrations import register_integrations
        register_integrations(
            toml=toml,
            rails=MyRailsIntegration(),
            sep31_receiver=MySEP31ReceiverIntegration(),
          #  deposit=MyDepositIntegration(),
          #  withdrawal=MyWithdrawIntegration()
        )
