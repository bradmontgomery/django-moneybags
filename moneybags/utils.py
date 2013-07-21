from collections import namedtuple
from csv import reader
from decimal import Decimal, InvalidOperation


def load_transactions_from_csv(path_to_csv_file):
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
        return Decimal('0')
