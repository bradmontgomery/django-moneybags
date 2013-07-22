from collections import namedtuple
from csv import reader
from decimal import Decimal, InvalidOperation

from .settings import (
    TRANSACTION_TYPE_DEBIT,
    TRANSACTION_TYPE_CREDIT,
)


def load_csv_data(path_to_csv_file):
    """Loads data from a CSV file, returning a list of ``namedtuple``s
    containing transaction data.

    The CSV should be organized like a checkbook register with the following
    columns:

    * Date
    * Check Number
    * Description
    * Debit Amount
    * Credit Amount

    """
    fields = 'date, check, description, debit, credit'
    Transaction = namedtuple('Transaction', fields)

    csv_reader = reader(open(path_to_csv_file, "rb"))
    return map(Transaction._make, csv_reader)


def to_decimal(value):
    """Convert a string value to a Decimal. Remove any $ characters."""
    value = value.replace("$", "")
    try:
        value = Decimal(value)
    except InvalidOperation:
        return None


def create_transactions(account, transactions):
    """Create ``Transaction`` objects for the given account (an ``Account``
    instance) and the given list of transaction data -- this should be a
    list of ``namedtuple``s like that returned from ``load_csv_data``.

    Note: This creates all Transactions as "pending".

    """

    for trans in transactions:
        # Check for credits or Debits; One of these should be None
        debit = to_decimal(trans.debit)
        credit = to_decimal(trans.credit)
        if debit is None:
            # we've got a credit
            amount = credit
            trans_type = TRANSACTION_TYPE_CREDIT
        elif credit is None:
            # We've got a debit
            amount = debit
            trans_type = TRANSACTION_TYPE_DEBIT
        else:
            # This is an invalid transaction, skip it.
            amount = None

        try:
            check_no = int(trans.check)
        except ValueError:
            check_no = None

        if amount is not None:
            account.transaction_set.create(
                date=trans.date,
                check_no=check_no,
                description=trans.description,
                amount=amount,
                pending=True,
                transaction_type=trans_type
            )
