from polaris.models import Asset
from rest_framework.request import Request


def toml(request: Request):
    asset_list = Asset.objects.all()
    curr_list = []
    for asset in asset_list:
        curr_list.append({
            "code": asset.code,
            "issuer": asset.issuer,
            "status": "test",
            "display_decimals" : 2,
            "name": "test",
            "desc": "Fake asset on testnet"
        })

    return {
        "DOCUMENTATION": {
            "ORG_NAME": "Relevance Lab",
            "ORG_URL": "https://relevancelab.com/"
        },
        "PRINCIPALS": [{
            "name": "Rahul Kumar"
        },
        ],
        "CURRENCIES": curr_list
    }
