from django.core.validators import URLValidator
from polaris import settings
from polaris.integrations import CustomerIntegration
from polaris.models import Transaction
from polaris.sep10.token import SEP10Token
from polaris.sep10.utils import validate_sep10_token
from polaris.utils import render_error_response, extract_sep9_fields, getLogger, make_memo
from rest_framework.decorators import api_view, renderer_classes, parser_classes

from rest_framework.request import Request
from typing import Dict, Optional, List
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from sep_12.models import Customer,CustomerStellarAccount
from polaris.integrations import registered_customer_integration as rci
from rest_framework.response import Response

logger = getLogger(__name__)


class MyCustomerIntegration(CustomerIntegration):

    @staticmethod
    @validate_sep10_token()
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
                if "email_address" not in params or "first_name" not in params or "last_name" not in params \
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

    @staticmethod
    @validate_sep10_token()
    def get(self, token: SEP10Token, request: Request, params: Dict, *args, **kwargs) -> Response:
        """ get customer info api implemented for sep 12"""
        if params.get("id"):
            try:
                response_data = rci.get(
                    token=token,
                    request=request,
                    params={
                        "id": request.GET.get("id"),
                        "account": request.GET.get("account"),
                        "type": request.GET.get("type"),
                        "lang": request.GET.get("lang"),
                    },
                )
            except ValueError as e:
                return render_error_response(str(e), status_code=400)
            except ObjectDoesNotExist as e:
                return render_error_response(str(e), status_code=404)

            try:
                validate_response_data(response_data)
            except ValueError:
                logger.exception(
                    "An exception was raised validating GET /customer response"
                )
                return render_error_response(
                    _("unable to process request."), status_code=500
                )

        return Response(response_data)

    # delete
    @validate_sep10_token()
    def delete(self, SEP10Token, request, account, memo, memo_type, *arg, **kwargs):

        account = CustomerStellarAccount.objects.get(account=account, memo=memo, memo_type=memo_type)

        if account:
            account.delete()
        else:

            raise ObjectDoesNotExist("account does not exit")

    @api_view(["PUT"])
    @validate_sep10_token()
    def callback(self, token: SEP10Token, request: Request) -> Response:
        if request.data.get("id"):
            if not isinstance(request.data.get("id"), str):
                return render_error_response("bad ID value, expected str")
            elif (
                    request.data.get("account")
                    or request.data.get("memo")
                    or request.data.get("memo_type")
            ):
                return render_error_response("requests with 'id' cannot also have 'account', 'memo', or 'memo_type'",
                                             status_code=400)
        elif request.data.get("account") != (token.muxed_account or token.account):
            return render_error_response("The account specified does not match authorization token", status_code=403)
        elif (
                token.memo
                and request.data.get("memo")
                and (
                        str(token.memo) != str(request.data.get("memo"))
                        or request.data.get("memo_type") != Transaction.MEMO_TYPES.id
                )
        ):
            return render_error_response(
                "The memo specified does not match the memo ID authorized via SEP-10",
                status_code=403,
            )

        try:
            # validate memo and memo_type
            make_memo(request.data.get("memo"), request.data.get("memo_type"))
        except (ValueError, TypeError):
            return render_error_response(_("invalid 'memo' for 'memo_type'"))

        memo = request.data.get("memo") or token.memo
        memo_type = None
        if memo:
            memo_type = request.data.get("memo_type") or Transaction.MEMO_TYPES.id
            if memo_type == Transaction.MEMO_TYPES.id:
                memo = int(memo)

        callback_url = request.data.get("url")
        if not callback_url:
            return render_error_response("callback 'url' required", status_code=500)
        schemes = ["https"] if not settings.LOCAL_MODE else ["https", "http"]
        try:
            URLValidator(schemes=schemes)(request.data.get("url"))
        except ValidationError:
            return render_error_response("'url' must be a valid URL")

        try:
            rci.callback(
                token=token,
                request=request,
                params={
                    "id": request.data.get("id"),
                    "account": token.muxed_account or token.account,
                    "memo": memo,
                    "memo_type": memo_type,
                    "url": callback_url,
                },
            )
        except ValueError as e:
            return render_error_response(str(e), status_code=400)
        except ObjectDoesNotExist as e:
            return render_error_response(str(e), status_code=404)
        except NotImplementedError:
            return render_error_response("not implemented", status_code=501)

        return Response({"success": True})


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
