from django.db import models
from model_utils import Choices


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(unique=True, max_length=56)
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)
    additional_name = models.CharField(max_length=254, null=True, blank=True)
    bank_number = models.CharField(max_length=254, null=True, blank=True)
    bank_account_number = models.CharField(max_length=254, null=True, blank=True)


class CustomerStellarAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    stellar_account = models.CharField(max_length=56)
    muxed_account = models.TextField(null=True, blank=True)
    memo = models.TextField(null=True, blank=True)
    memo_type = models.CharField(
        choices=Choices("text", "id", "hash"),
        max_length=4,
        null=True,
        blank=True
    )

    models.UniqueConstraint(
        fields=["account", "muxed_account", "memo", "memo_type"],
        name="account_memo_constraint"
    )
