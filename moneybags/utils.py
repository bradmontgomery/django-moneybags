from collections import namedtuple
from csv import reader
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.shortcuts import render_to_response
from django.template import RequestContext
from re import sub as regex_sub
from sys import stdout


from .settings import (
    TRANSACTION_TYPE_DEBIT,
    TRANSACTION_TYPE_CREDIT,
)


def paginate_queryset(request, queryset, num_items=50, page_var='page'):
    """Given a queryset of objects, return paginated results.

    # ``request`` -- an HTTPRequest object; Used to retrieve given page numbers
    * ``queryset`` -- a QuerySet of model objects (or any iterable)
    * ``num_items`` -- the number of items to show, per page.
    * ``page_var`` -- the name of the querystring variable for the given page

    """
    paginator = Paginator(queryset, num_items)
    page = request.GET.get(page_var)
    try:
        # Generate the specified page of results
        results = paginator.page(page)
    except PageNotAnInteger:
        # Generate the 1st page of results
        results = paginator.page(1)
    except EmptyPage:
        # Generate the last page of results
        results = paginator.page(paginator.num_pages)
    return results


def rtr(request, template, data):
    """A shortcut for ``render_to_response`` using ``RequestContext``."""
    args = (template, data)
    kwargs = {"context_instance": RequestContext(request)}
    return render_to_response(*args, **kwargs)


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


def to_decimal(value, formatting_chars=['$', ',']):
    """Convert a string value to a Decimal. Remove any $ characters."""
    # Remove any formatting and/or special characters
    pattern = "[{0}]".format('|'.join(formatting_chars))
    value = regex_sub(pattern, '', value)

    # Now, attempt a Decimal conversion.
    try:
        value = Decimal(value)
    except InvalidOperation:
        value = None
    return value


def create_transactions(account, transactions, date_format_string='%m/%d/%Y',
                        pending=True, verbose=False):
    """Create ``Transaction`` objects for the given Account and the given
    list of transaction data.

    * ``account`` -- The ``Account`` under which to group Transactions.
    * ``transactions`` -- a list of ``namedtuple``s like that returned from
      ``load_csv_data``.
    * ``pending`` -- (default is True) Whether or not to create pending
      Transactions
    * ``date_format_string`` -- used by strptime; the format to convert a
      string into a datetime object. Default is '%m/%d/%Y'
    * ``verbose`` -- (default is False) Print info to stdout upon creation of
      each transaction.

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
            if verbose:
                stdout.write("---> Amount is NONE for {0}!\n".format(trans))

        try:
            check_no = int(trans.check)
        except ValueError:
            check_no = None

        if amount:
            account.transaction_set.create(
                date=datetime.strptime(trans.date, date_format_string),
                check_no=check_no,
                description=trans.description,
                amount=amount,
                pending=pending,
                transaction_type=trans_type
            )
            if verbose:
                m = "Created: {date} / {desc} / ${amt}\n".format(
                    date=trans.date,
                    desc=trans.description,
                    amt=amount
                )
                stdout.write(m)
