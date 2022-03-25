from polaris.integrations import CustomerIntegration
from polaris.sep10.token import SEP10Token
from polaris.utils import extract_sep9_fields, getLogger
from django.utils.translation import gettext as _
from rest_framework.request import Request
from typing import Dict
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, CustomerStellarAccount
from stellar_sdk import MuxedAccount

logger = getLogger(__name__)


class MyCustomerIntegration(CustomerIntegration):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required_fields = [
            "account",
            "first_name",
            "last_name",
            "email_address",
            "bank_account_number",
            "bank_number",
        ]
        self.accepted = {"status": "ACCEPTED"}
        self.needs_basic_info = {
            "status": "NEEDS_INFO",
            "fields": {
                "first_name": {
                    "description": "first name of the customer",
                    "type": "string",
                },
                "last_name": {
                    "description": "last name of the customer",
                    "type": "string",
                },
                "email_address": {
                    "description": "email address of the customer",
                    "type": "string",
                },
            },
        }
        self.needs_bank_info = {
            "status": "NEEDS_INFO",
            "fields": {
                "bank_account_number": {
                    "description": "bank account number of the customer",
                    "type": "string",
                },
                "bank_number": {
                    "description": "routing number of the customer",
                    "type": "string",
                },
            },
        }
        self.needs_all_info = {
            "status": "NEEDS_INFO",
            "fields": {
                "first_name": {
                    "description": "first name of the customer",
                    "type": "string",
                },
                "last_name": {
                    "description": "last name of the customer",
                    "type": "string",
                },
                "email_address": {
                    "description": "email address of the customer",
                    "type": "string",
                },
                "bank_account_number": {
                    "description": "bank account number of the customer",
                    "type": "string",
                },
                "bank_number": {
                    "description": "routing number of the customer",
                    "type": "string",
                },
            },
        }

    def put(self, token: SEP10Token, request: Request, params: Dict, *args, **kwargs) -> Dict:
        if params.get("id"):
            user = Customer.objects.filter(id=params.get("id")).first()
            if not user:
                raise ObjectDoesNotExist("customer not found")
        else:
            stellar_account = params["account"]
            muxed_account = None
            account = CustomerStellarAccount.objects.filter(stellar_account=stellar_account).first()
            if not account:
                if "email_address" not in params or "first_name" not in params or "last_name" not in params:
                    raise ValueError(
                        "'first_name', 'last_name' and 'email_address' are required."
                    )
                user = Customer.objects.filter(email=params.get('email_address')).first()
                if not user:
                    user = Customer.objects.create(
                        first_name=params["first_name"],
                        last_name=params["last_name"],
                        email=params["email_address"],
                        bank_number=params.get("bank_number"),
                        bank_account_number=params.get("bank_account_number"),
                        # phone=params.get('phone_number')
                    )
                CustomerStellarAccount.objects.create(
                    customer=user,
                    stellar_account=stellar_account,
                    muxed_account=muxed_account,
                    memo=params['memo'],
                    memo_type=params['memo_type']
                )
            else:
                user = account.customer
        if (user.email != params.get("email_address") and
                Customer.objects.filter(email=params.get("email_address")).exists()):
            raise ValueError("Email Taken")
        user.email = params.get("email_address") or user.email
        user.first_name = params.get("first_name") or user.first_name
        user.last_name = params.get("last_name") or user.last_name
        user.additional_name = params.get("additional_name") or user.additional_name
        user.bank_number = params.get("bank_number") or user.bank_number
        user.bank_account_number = (
                params.get("bank_account_number") or user.bank_account_number
        )
        user.save()
        return str(user.id)

    def get(self, token: SEP10Token, request: Request, params: Dict, *args, **kwargs) -> Dict:
        user = None
        if params.get("id"):
            user = Customer.objects.filter(id=params["id"]).first()
            if not user:
                raise ObjectDoesNotExist(_("customer not found"))
        elif params.get("account"):
            if params["account"].startswith("M"):
                stellar_account = MuxedAccount.from_account(
                    params["account"]
                ).account_id
                muxed_account = params["account"]
            else:
                stellar_account = params["account"]
                muxed_account = None
            account = CustomerStellarAccount.objects.filter(
                stellar_account=stellar_account,
                muxed_account=muxed_account,
                memo=params.get("memo"),
                memo_type=params.get("memo_type"),
            ).first()
            user = account.user if account else None

        if not user:
            if params.get("type") in ["sep6-deposit", "sep31-sender", "sep31-receiver"]:
                return self.needs_basic_info
            elif params.get("type") in [None, "sep6-withdraw"]:
                return self.needs_all_info
            else:
                raise ValueError(
                    "invalid 'type'. see /info response for valid values."
                )

        response_data = {"id": str(user.id)}
        basic_info_accepted = {
            "provided_fields": {
                "first_name": {
                    "description": "first name of the customer",
                    "type": "string",
                    "status": "ACCEPTED",
                },
                "last_name": {
                    "description": "last name of the customer",
                    "type": "string",
                    "status": "ACCEPTED",
                },
                "email_address": {
                    "description": "email address of the customer",
                    "type": "string",
                    "status": "ACCEPTED",
                },
            }
        }
        if (user.bank_number and user.bank_account_number) or (
                params.get("type") in ["sep6-deposit", "sep31-sender", "sep31-receiver"]
        ):
            response_data.update(self.accepted)
            response_data.update(basic_info_accepted)
            if user.bank_number and user.bank_account_number:
                response_data["provided_fields"].update(
                    {
                        "bank_account_number": {
                            "description": "bank account number of the customer",
                            "type": "string",
                            "status": "ACCEPTED",
                        },
                        "bank_number": {
                            "description": "routing number of the customer",
                            "type": "string",
                            "status": "ACCEPTED",
                        },
                    }
                )
        elif params.get("type") in [None, "sep6-withdraw"]:
            response_data.update(basic_info_accepted)
            response_data.update(self.needs_bank_info)
        else:
            raise ValueError(_("invalid 'type'. see /info response for valid values."))
        return response_data

    def delete(self, token: SEP10Token, request: Request, account: str, memo: str, memo_type: str, *args, **kwargs):
        if account:
            customer_id = CustomerStellarAccount.objects.filter(stellar_account=account).first()
            if customer_id is None:
                raise ObjectDoesNotExist("account not found")
            else:
                customer_id.delete()


def validate_response_data(data: Dict):
    attrs = ["fields", "id", "message", "status", "provided_fields"]
    if not data:
        raise ValueError("empty response from SEP-12 get() integration")
    elif any(f not in attrs for f in data):
        raise ValueError(
            f"unexpected attribute included in GET /customer response. "
            f"Accepted attributes: {attrs}"
        )
    elif "id" in data and not isinstance(data["id"], str):
        raise ValueError("customer IDs must be strings")
    accepted_statuses = ["ACCEPTED", "PROCESSING", "NEEDS_INFO", "REJECTED"]
    if not data.get("status") or data.get("status") not in accepted_statuses:
        raise ValueError("invalid status in SEP-12 GET /customer response")
    elif (
            any([f.get("optional") is False for f in data.get("fields", {}).values()])
            and data.get("status") == "ACCEPTED"
    ):
        raise ValueError(
            "all required 'fields' must be provided before a customer can be 'ACCEPTED'"
        )
    if data.get("fields"):
        validate_fields(data.get("fields"))
    if data.get("provided_fields"):
        validate_fields(data.get("provided_fields"), provided=True)
    if data.get("message") and not isinstance(data["message"], str):
        raise ValueError(
            "invalid message value in SEP-12 GET /customer response, should be str"
        )


def validate_fields(fields: Dict, provided=False):
    if not isinstance(fields, Dict):
        raise ValueError(
            "invalid fields type in SEP-12 GET /customer response, should be dict"
        )
    if len(extract_sep9_fields(fields)) < len(fields):
        raise ValueError("SEP-12 GET /customer response fields must be from SEP-9")
    accepted_field_attrs = [
        "type",
        "description",
        "choices",
        "optional",
        "status",
        "error",
    ]
    accepted_types = ["string", "binary", "number", "date"]
    accepted_statuses = [
        "ACCEPTED",
        "PROCESSING",
        "REJECTED",
        "VERIFICATION_REQUIRED",
    ]
    for key, value in fields.items():
        if not set(value.keys()).issubset(set(accepted_field_attrs)):
            raise ValueError(
                f"unexpected attribute in '{key}' object in SEP-12 GET /customer response, "
                f"accepted values: {', '.join(accepted_field_attrs)}"
            )
        if not value.get("type") or value.get("type") not in accepted_types:
            raise ValueError(
                f"bad type value for '{key}' in SEP-12 GET /customer response"
            )
        elif not (
                value.get("description") and isinstance(value.get("description"), str)
        ):
            raise ValueError(
                f"bad description value for '{key}' in SEP-12 GET /customer response"
            )
        elif value.get("choices") and not isinstance(value.get("choices"), list):
            raise ValueError(
                f"bad choices value for '{key}' in SEP-12 GET /customer response"
            )
        elif value.get("optional") and not isinstance(value.get("optional"), bool):
            raise ValueError(
                f"bad optional value for '{key}' in SEP-12 GET /customer response"
            )
        elif not provided and value.get("status"):
            raise ValueError(
                f"'{key}' object in 'fields' object cannot have a 'status' property"
            )
        elif (
                provided
                and value.get("status")
                and value.get("status") not in accepted_statuses
        ):
            raise ValueError(
                f"bad field status value for '{key}' in SEP-12 GET /customer response"
            )
        elif not provided and value.get("error"):
            raise ValueError(
                f"'{key}' object in 'fields' object cannot have 'error' property"
            )
        elif (
                provided and value.get("error") and not isinstance(value.get("error"), str)
        ):
            raise ValueError(
                f"bad error value for '{key}' in SEP-12 GET /customer response"
            )


