from polaris.integrations import CustomerIntegration
from polaris.sep10.token import SEP10Token
from rest_framework.request import Request
from typing import Dict, Optional, List
from django.core.exceptions import ObjectDoesNotExist
from sep_12.models import Customer, CustomerStellarAccount


class MyCustomerIntegration(CustomerIntegration):
    def put(self, token: SEP10Token, request: Request, params: Dict, *args, **kwargs) -> str:
        if params.get("id"):
            user = Customer.objects.get(id=params.get("id"))
            if not user:
                raise ObjectDoesNotExist("customer not found with id %s", params.get("id"))
        else:
            stellar_account = params["account"]
            muxed_account = None
            account = CustomerStellarAccount.objects.get(
                account=stellar_account,
                muxed_account=muxed_account,
                memo=params.get("memo"),
                memo_type=params.get("memo_type")
            )
            if not account:
                if "email_address" not in params or "first_name" not in params or "last_name" not in params\
                        or "phone_number" not in params:
                    raise ValueError(
                        "'first_name', 'last_name', 'phone_number' and 'email_address' are required."
                    )
                user = Customer.objects.get(email=params.get('email'))
                if not user:
                    user = Customer.objects.create(
                        first_name=params["first_name"],
                        last_name=params["last_name"],
                        email=params["email_address"],
                        bank_number=params.get("bank_number"),
                        bank_account_number=params.get("bank_account_number"),
                    )
                account = CustomerStellarAccount.objects.create(
                    user=user,
                    account=stellar_account,
                    muxed_account=muxed_account,
                    memo=params['memo'],
                    memo_type=params['memo_type']
                )
            else:
                user = account.user
        if (user.email != params.get("email") and
                Customer.objects.filter(email=params.get("email_address")).exists()):
            raise ValueError("Email Taken")
        user.email = params.get("email_address") or user.email
        user.first_name = params.get("first_name") or user.first_name
        user.last_name = params.get("last_name") or user.last_name
        user.bank_number = params.get("bank_number") or user.bank_number
        user.bank_account_number = (
                params.get("bank_account_number") or user.bank_account_number
        )
        user.save()
        return str(user.id)

    def get(self, token: SEP10Token, request: Request, params: Dict, *args, **kwargs) -> Dict:
        if params.get("id"):
            user = Customer.objects.get(id=params.get("id"))
            if not user:
                raise ObjectDoesNotExist("customer not found with id %s", params.get("id"))
        else:
            return {}
        
    # delete
    def delete(self,SEP10Token,request,account,memo,memo_type,*arg,**kwargs):

        account = CustomerStellarAccount.objects.get(account=account,memo=memo,memo_type=memo_type)
        if account:
            account.delete()
        else:
            raise ObjectDoesNotExist("account does not exit")