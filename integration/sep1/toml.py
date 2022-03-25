from polaris.models import Asset
from rest_framework.request import Request


def toml(request: Request):
    asset = Asset.objects.first()
    return {
        "DOCUMENTATION": {
            "ORG_NAME": "Relevance Lab",
            "ORG_URL": "https://relevancelab.com/"
        },
        "PRINCIPALS": [{
            "name": "Rahul Kumar"
        },
        ],
        "CURRENCIES": [
            {
                "code": asset.code,
                "issuer": asset.issuer,
                "status": "test",
                "display_decimals": 2,
                "name": "test",
                "desc": "Fake asset on testnet"
            }
        ]
    }
