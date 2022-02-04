from decimal import Decimal
from typing import Optional, Dict, List

from django import forms
from django.utils.translation import gettext as _
from polaris.sep10.token import SEP10Token
from polaris.templates import Template
from rest_framework.request import Request

from polaris.integrations import DepositIntegration
from polaris.models import Asset, Transaction


class MyDepositIntegration(DepositIntegration):
    def after_deposit(self, transaction: Transaction, *args: List, **kwargs: Dict):
        pass

    def content_for_template(self, request: Request, template: Template, form: Optional[forms.Form] = None,
                             transaction: Optional[Transaction] = None, *args: List, **kwargs: Dict) -> Optional[Dict]:
        pass

    def after_form_validation(self, request: Request, form: forms.Form, transaction: Transaction, *args: List,
                              **kwargs: Dict):
        pass

    def interactive_url(self, request: Request, transaction: Transaction, asset: Asset, amount: Optional[Decimal],
                        callback: Optional[str], *args: List, **kwargs: Dict) -> Optional[str]:
        pass

    def save_sep9_fields(self, token: SEP10Token, request: Request, stellar_account: str, fields: Dict,
                         language_code: str, muxed_account: Optional[str] = None, account_memo: Optional[str] = None,
                         account_memo_type: Optional[str] = None, *args: List, **kwargs: Dict):
        pass

    def process_sep6_request(self, token: SEP10Token, request: Request, params: Dict, transaction: Transaction,
                             *args: List, **kwargs: Dict) -> Dict:
        pass

    def create_channel_account(self, transaction: Transaction, *args: List, **kwargs: Dict):
        pass

    def patch_transaction(self, token: SEP10Token, request: Request, params: Dict, transaction: Transaction,
                          *args: List, **kwargs: Dict):
        pass
