from datetime import date

from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404, redirect

from models import Account, Transaction, RecurringTransaction
from forms import AccountForm, TransactionForm, TransactionCheckBoxForm
from forms import RecurringTransactionForm, TransactionReportForm
from forms import modelform_handler
from utils import paginate_queryset, rtr


@login_required
def create_transaction(request, account_slug):
    """Create a new Transaction associated with a specified Account."""
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    form, trans = modelform_handler(request, TransactionForm, commit=False)
    if trans:
        trans.account = account
        trans.save()
        if trans.recurring:
            return redirect(trans.get_recurring_transaction_url())
        return redirect(trans.account)

    data = {'account': account, 'form': form, 'transaction': trans}
    return rtr(request, 'moneybags/create_transaction.html', data)


@login_required
def transaction_report(request, account_slug):
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    transactions = None
    if request.method == "POST":
        form = TransactionReportForm(request.POST)
        if form.is_valid():
            transactions = form.get_matching_transactions()
    else:
        form = TransactionReportForm()

    data = {'account': account, 'form': form, 'transactions': transactions}
    return rtr(request, 'moneybags/transaction_report.html', data)


@login_required
def recurring_transaction(request, account_slug, transaction_id):
    """Create or Update a RecurringTransaction, given a Transaction's `id`."""
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction_id,
        account=account)
    recurring_transaction = transaction.get_recurring_transaction()

    form, updated_transaction = modelform_handler(
        request,
        RecurringTransactionForm,
        instance=recurring_transaction,
        commit=True
    )
    if updated_transaction:  # Transaction was updated, redirect to it.
        return redirect(updated_transaction)

    data = {'account': account, 'transaction': transaction, 'form': form}
    return rtr(request, 'moneybags/recurring_transaction.html', data)


@login_required
def update_recurring_transaction(request, account_slug,
                                 recurring_transaction_id):
    """Update a RecurringTransaction."""
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    recurring_transaction = get_object_or_404(RecurringTransaction,
        pk=recurring_transaction_id, account=account)

    form, updated_transaction = modelform_handler(
        request,
        RecurringTransactionForm,
        instance=recurring_transaction,
        commit=True
    )
    if updated_transaction:  # Transaction was updated, redirect to it.
        return redirect(updated_transaction)

    data = {
        'account': account,
        'form': form,
        'recurring_transaction': recurring_transaction
    }
    return rtr(request, 'moneybags/update_recurring_transaction.html', data)


@login_required
def list_accounts(request):
    """Lists Accounts owned by the authenticated User."""
    data = {'accounts': Account.objects.filter(owner=request.user)}
    return rtr(request, 'moneybags/list_accounts.html', data)


@login_required
def create_account(request):
    """Create a new ``Account`` owned by the authenticated User."""
    form, acct = modelform_handler(request, AccountForm, commit=False)
    if acct:
        acct.owner = request.user
        acct.save()
        return redirect(acct)
    data = {'form': form}
    return rtr(request, 'moneybags/create_account.html', data)


@login_required
def detail_account(request, account_slug):
    """List recent debits, credits, and any upcoming recurring transactions."""
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    balance = account.get_balance()

    today = date.today()

    # TODO: for recurring transactions to automatically get dumped into the
    # "Transaction" list, we've got to run the ``create_transactions``
    # Management command.  Now, that'll create a Transaction based on
    # RecurringTranscations,
    #
    # BUT, the recurringTransaction will still have the wrong date. Either the
    # model, or the managment command needs to update it's due date,

    transactions = Transaction.objects.filter(account=account)
    recurring_transactions = RecurringTransaction.objects.filter(
        due_date__gte=today,
        account=account
    )

    # Create a FormSet using a TransactionCheckBoxForm for each Transaction
    # listed.
    TransactionFormSet = formset_factory(TransactionCheckBoxForm, extra=0)
    initial_data = [{'value': False, 'object_id': t.id} for t in transactions]
    formset = TransactionFormSet(initial=initial_data)

    # Paginate the list of Transactions
    transactions = paginate_queryset(request, transactions)

    data = {
        'account': account,
        'balance': balance,
        'formset': formset,
        'overdrawn': not balance > 0,
        'recurring_transactions': recurring_transactions,
        'today': today,
        'transactions': transactions,
    }
    return rtr(request, 'moneybags/detail_account.html', data)


@login_required
def update_transactions(request, account_slug):
    """Update one or more Transactions for the given Account. The types of
    updates may include:

    - deleting transactions
    - changes to pending status.

    """
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)

    cleaned_data = None
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action', None)

        TransactionFormSet = formset_factory(TransactionCheckBoxForm, extra=0)
        formset = TransactionFormSet(request.POST, request.FILES)

        if action and formset.is_valid():
            cleaned_data = formset.cleaned_data
            # Cleaned data is a list of dictionaries of the form:
            #   {'object_id':X, 'value':False }
            #
            # Perform the action on the objects whose values are `True`
            ids = [d['object_id'] for d in cleaned_data if d['value']]

            # NOTE: the following perform BULK operations, so they don't
            # execute Transaction.save()
            if action == 'delete':
                Transaction.objects.filter(id__in=ids).delete()
            elif action == 'remove-pending':
                Transaction.objects.filter(id__in=ids).update(pending=False)

    return redirect(account)


@login_required
def detail_transaction(request, account_slug, transaction_id):
    """Show all the details associated with a single Transaction."""
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    transaction = get_object_or_404(Transaction, account=account,
        id=transaction_id)

    similar_transactions = transaction.get_similar_transactions()
    data = {
        'account': account,
        'transaction': transaction,
        'similar_transactions': similar_transactions
    }
    return rtr(request, 'moneybags/detail_transaction.html', data)
