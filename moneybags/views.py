from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404, redirect

from models import Account, Transaction, RecurringTransaction
from forms import AccountForm, TransactionForm, TransactionCheckBoxForm
from forms import RecurringTransactionForm, modelform_handler
from utils import rtr


@login_required
def new_transaction(request, account_slug):
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    form, trans = modelform_handler(request, TransactionForm, commit=False)
    if trans:
        trans.account = account
        trans.save()
        if trans.recurring:
            return redirect(trans.get_recurring_transaction_url())
        return redirect(trans.account)

    data = {'account': account, 'form': form, 'transaction': trans}
    return rtr(request, 'moneybags/new_transaction.html', data)


@login_required
def recurring_transaction(request, account_slug, transaction_id):
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
def edit_recurring_transaction(request, account_slug,
                               recurring_transaction_id):
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
    return rtr(request, 'moneybags/edit_recurring_transaction.html', data)


@login_required
def account_list(request):
    data = {'accounts': Account.objects.filter(owner=request.user)}
    return rtr(request, 'moneybags/account_list.html', data)


@login_required
def account_create(request):
    """Create a new ``Account`` owned by the authenticated User."""
    form, acct = modelform_handler(request, AccountForm, commit=False)
    if acct:
        acct.owner = request.user
        acct.save()
        return redirect(acct)
    data = {'form': form}
    return rtr(request, 'moneybags/account_create.html', data)


@login_required
def account_detail(request, account_slug):
    """List recent debits, credits, and any upcoming recurring transactions."""
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    balance = account.get_balance()

    # Display the 30 days worth of transactions.
    today = date.today()
    since = timedelta(days=-30) + today

    #TODO:
    # for recurring transactions to automatically get dumped into the
    # "Transaction" list, we've got to run the
    # ``moneybags_create_transactions_due_today`` Management command.  Now,
    # that'll create a Transaction based on RecurringTranscations,
    #
    # BUT, the recurringTransaction will still have the wrong date. Either the
    # model, or the managment command needs to update it's due date,
    transactions = Transaction.objects.filter(date__gte=since, account=account)
    transactions = transactions.order_by('-date', 'id')
    recurring_transactions = RecurringTransaction.objects.filter(
        due_date__gte=today, account=account).order_by('-due_date', 'id')

    # Create a FormSet using a TransactionCheckBoxForm for each Transaction
    # listed.
    TransactionFormSet = formset_factory(TransactionCheckBoxForm, extra=0)
    initial_data = [{'value':False, 'object_id':t.id} for t in transactions]
    formset = TransactionFormSet(initial=initial_data)

    data = {
        'account': account,
        'balance': balance,
        'formset': formset,
        'overdrawn': not balance > 0,
        'recurring_transactions': recurring_transactions,
        'since': since,
        'today': today,
        'transactions': transactions,
    }
    return rtr(request, 'moneybags/account_detail.html', data)


@login_required
def account_update(request, account_slug):
    """Handle POST from account_detail, and update selected transactions:

    - delete
    - set as pending/not pending

    Then redirect to account detail.
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
def transaction_detail(request, account_slug, transaction_id):
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
    return rtr(request, 'moneybags/transaction_detail.html', data)
