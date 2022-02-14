from decimal import Decimal
from typing import Dict, List, Optional

from django import forms
from polaris.integrations import DepositIntegration
from polaris.models import Transaction, Asset
from polaris.sep10.token import SEP10Token
from polaris.templates import Template
from rest_framework.request import Request
from polaris.sep24.utils import generate_interactive_jwt
from urllib.parse import urlencode
from django.urls import reverse
from django.http import QueryDict
from polaris.integrations.forms import TransactionForm
from polaris.sep24.utils import interactive_url as i_url
from polaris import settings as pst
import traceback

class MyDepositIntegration(DepositIntegration):
    def after_deposit(self, transaction: Transaction, *args: List, **kwargs: Dict):
        raise NotImplementedError("NOT IMPLEMENTED")

    def content_for_template(self, request: Request, template: Template, form: Optional[forms.Form] = None,
                             transaction: Optional[Transaction] = None, *args: List, **kwargs: Dict) -> Optional[Dict]:
        raise NotImplementedError("NOT IMPLEMENTED")

    def after_form_validation(self, request: Request, form: forms.Form, transaction: Transaction, *args: List,
                              **kwargs: Dict):
        raise NotImplementedError("NOT IMPLEMENTED")

    def interactive_url(self, request: Request, transaction: Transaction, asset: Asset, amount: Optional[Decimal],
                        callback: Optional[str], *args: List, **kwargs: Dict) -> Optional[str]:

        #traceback.print_tb(tb=None, limit=None, file=None)
        traceback.print_exc()
        f_url = i_url(request=request, transaction_id=str(transaction.id), account=transaction.stellar_account,
                      memo=transaction.memo, op_type=pst.OPERATION_DEPOSIT, amount=transaction.amount_in,
                      asset_code=asset.code)
        #print(f_url.replace("localhost:8000","testanchor.relevancelab.com"))
        #return f_url.replace("localhost:8000","testanchor.relevancelab.com")

        return f_url
    def save_sep9_fields(self, token: SEP10Token, request: Request, stellar_account: str, fields: Dict,
                         language_code: str, muxed_account: Optional[str] = None, account_memo: Optional[str] = None,
                         account_memo_type: Optional[str] = None, *args: List, **kwargs: Dict):
        raise NotImplementedError("NOT IMPLEMENTED")

    def process_sep6_request(self, token: SEP10Token, request: Request, params: Dict, transaction: Transaction,
                             *args: List, **kwargs: Dict) -> Dict:
        raise NotImplementedError("NOT IMPLEMENTED")

    def create_channel_account(self, transaction: Transaction, *args: List, **kwargs: Dict):
        raise NotImplementedError("NOT IMPLEMENTED")

    def patch_transaction(self, token: SEP10Token, request: Request, params: Dict, transaction: Transaction,
                          *args: List, **kwargs: Dict):
        raise NotImplementedError("NOT IMPLEMENTED")

    def form_for_transaction(
            self,
            request: Request,
            transaction: Transaction,
            post_data: Optional[QueryDict] = None,
            amount: Optional[Decimal] = None,
            *args: List,
            **kwargs: Dict
    ) -> Optional[forms.Form]:

        if transaction.amount_in:
            # we've collected transaction info
            # and don't implement KYC by default
            return

        if post_data:
            return TransactionForm(transaction, post_data)
        else:
            return TransactionForm(transaction, initial={"amount": amount})


registered_deposit_integration = MyDepositIntegration()
