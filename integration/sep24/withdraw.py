from decimal import Decimal
from typing import Dict, List, Optional

from django import forms
from polaris.integrations import WithdrawalIntegration
from polaris.models import Transaction, Asset
from polaris.sep10.token import SEP10Token
from polaris.templates import Template
from rest_framework.request import Request
from polaris.sep24.utils import interactive_url as i_url
from polaris import settings as pst
from polaris.integrations.forms import TransactionForm
from django.http import QueryDict


class MyWithdrawIntegration(WithdrawalIntegration):
    def content_for_template(self, request: Request, template: Template, form: Optional[forms.Form] = None,
                             transaction: Optional[Transaction] = None, *args: List, **kwargs: Dict) -> Optional[Dict]:
        raise NotImplementedError("Not Implemented")

    def after_form_validation(self, request: Request, form: forms.Form, transaction: Transaction, *args: List,
                              **kwargs: Dict):
        raise NotImplementedError("Not Implemented")

    def interactive_url(self, request: Request, transaction: Transaction, asset: Asset, amount: Optional[Decimal],
                        callback: Optional[str], *args: List, **kwargs: Dict) -> Optional[str]:

        f_url = i_url(request=request, transaction_id=str(transaction.id), account=transaction.stellar_account,
                      memo=transaction.memo, op_type=pst.OPERATION_WITHDRAWAL, amount=transaction.amount_in,
                      asset_code=asset.code)
        print(f_url)
        return f_url

    def save_sep9_fields(self, token: SEP10Token, request: Request, stellar_account: str, fields: Dict,
                         language_code: str, muxed_account: Optional[str] = None, account_memo: Optional[str] = None,
                         account_memo_type: Optional[str] = None, *args: List, **kwargs: Dict):
        raise NotImplementedError("Not Implemented")

    def process_sep6_request(self, token: SEP10Token, request: Request, params: Dict, transaction: Transaction,
                             *args: List, **kwargs: Dict) -> Dict:
        raise NotImplementedError("Not Implemented")

    def patch_transaction(self, token: SEP10Token, request: Request, params: Dict, transaction: Transaction,
                          *args: List, **kwargs: Dict):
        raise NotImplementedError("Not Implemented")


    def form_for_transaction(
        self,
        request: Request,
        transaction: Transaction,
        post_data: Optional[QueryDict] = None,
        amount: Optional[Decimal] = None,
        *args: List,
        **kwargs: Dict
    ) -> Optional[forms.Form]:
        """
        .. _SEP-9: https://github.com/stellar/stellar-protocol/blob/master/ecosystem/sep-0009.md

        Same as ``DepositIntegration.form_for_transaction``

        :param request: a ``rest_framwork.request.Request`` object
        :param transaction: the ``Transaction`` database object
        :param post_data: the data included in the POST request body as a dictionary
        :param amount: a ``Decimal`` object the wallet may pass in the GET request.
            Use it to pre-populate your TransactionForm along with any SEP-9_
            parameters.
        """
        if transaction.amount_in:
            # we've collected transaction info
            # and don't implement KYC by default
            return
        elif post_data:
            return TransactionForm(transaction, post_data)
        else:
            return TransactionForm(transaction, initial={"amount": amount})