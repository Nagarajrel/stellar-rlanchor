from decimal import Decimal
from typing import Optional, Dict

from django.utils.translation import gettext as _
from rest_framework.request import Request

from polaris.integrations import SEP31ReceiverIntegration
from polaris.models import Asset, Transaction


class MySEP31ReceiverIntegration(SEP31ReceiverIntegration):
    def info(
        self,
        request: Request,
        asset: Asset,
        lang: Optional[str] = None,
        *args,
        **kwargs,
    ):
        return {
            "sep12": {
                "sender": {
                    "types": {
                        "sep31-sender": {
                            "description": "the basic type for sending customers"
                        }
                    }
                },
                "receiver": {
                    "types": {
                        "sep31-receiver": {
                            "description": "the basic type for receiving customers"
                        }
                    }
                },
            },
            "fields": {
                "transaction": {
                    "routing_number": {
                        "description": "routing number of the destination bank account"
                    },
                    "account_number": {
                        "description": "bank account number of the destination"
                    },
                },
            },
        }