from polaris.models import Transaction
from typing import List, Dict
from polaris.integrations import RailsIntegration
from django.db.models import QuerySet


class MyRailsIntegration(RailsIntegration):
    def poll_pending_deposits(self, pending_deposits: QuerySet) -> List[Transaction]:
        return list(pending_deposits)

    def poll_outgoing_transactions(
            self, transactions: QuerySet, *args: List, **kwargs: Dict
    ) -> List[Transaction]:
        return list(transactions)

    def execute_outgoing_transaction(self, transaction: Transaction):
        transaction.amount_fee = 0
        transaction.status = Transaction.STATUS.completed
        transaction.save()
