from datetime import date, timedelta

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.db.models import Q
from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.template.defaultfilters import slugify

from models import Account, Transaction, RecurringTransaction
from forms import AccountForm, TransactionForm, TransactionCheckBoxForm, RecurringTransactionForm, modelform_handler

@login_required
def new_transaction(request, account_slug):
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    form, object = modelform_handler(request, TransactionForm, commit=False)
    if object:
        object.account = account
        object.save()
        if object.recurring:
            return redirect(object.get_recurring_transaction_url())
        return redirect(object) # account detail

    data = {'account':account, 'form':form, 'object':object }
    return render_to_response('coffers/new_transaction.html', 
                               data,
                               context_instance=RequestContext(request))

@login_required
def recurring_transaction(request, account_slug, transaction_id):
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction_id, account=account)
    recurring_transaction = transaction.get_recurring_transaction()

    if recurring_transaction:
        form, object = modelform_handler(request, RecurringTransactionForm, instance=recurring_transaction, commit=True)
        if object:
            return redirect(object)

        data = {'account':account, 'form':form, 'transaction':transaction  }
    else:
        raise Http404

    return render_to_response('coffers/recurring_transaction.html', 
                               data,
                               context_instance=RequestContext(request))

@login_required
def account_list(request):
    accounts = Account.objects.filter(owner=request.user)
    return render_to_response('coffers/account_list.html', 
                               {'accounts':accounts}, 
                               context_instance=RequestContext(request))

@login_required
def account_create(request):
    """ create a new account """ 
    form, object = modelform_handler(request, AccountForm, commit=False)
    if object:
        object.owner = request.user
        object.save()
        return redirect(object)
    return render_to_response('coffers/account_create.html', 
                               {'form':form}, 
                               context_instance=RequestContext(request))

@login_required
def account_detail(request, account_slug):
    """
    List "recent" debits, credits, and any "upcoming" recurring transactions
    """
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    # get the balance of all Transactions.
    balance = sum(list(Transaction.objects.filter(account=account).values_list('amount', flat=True)))
    
    # Display the 30 days worth of transactions.
    today = date.today()
    since = timedelta(days=-30) + today

    transactions = Transaction.objects.filter(date__gte=since, account=account).order_by('-date', 'id')
    recurring_transactions = RecurringTransaction.objects.filter(due_date__gte=today)
    
    # Create a FormSet using a TransactionCheckBoxForm for each Transaction listed.
    TransactionFormSet = formset_factory(TransactionCheckBoxForm, extra=0)
    initial_data = [{'value':False, 'object_id':t.id} for t in transactions]
    formset = TransactionFormSet(initial=initial_data)

    data = {'account':account, 'transactions': transactions,
            'recurring_transactions':recurring_transactions,
            'today':today, 'since':since, 'balance':balance,
            'formset':formset, 
           }
    return render_to_response('coffers/account_detail.html', 
                              data,
                              context_instance=RequestContext(request))

@login_required
def account_update(request, account_slug):
    """ 
    Handle POST from account_detail, and update selected transactions:
    
    - delete
    - set as pending/not pending
    
    Then redirect to account detail 
    """ 
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
   
    cleaned_data = None
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action', None)

        #TODO: the next 3 lines are the same as in account_detail
        today = date.today()
        since = timedelta(days=-30) + today
        transactions = Transaction.objects.filter(date__gte=since, account=account).order_by('-date', 'id')

        TransactionFormSet = formset_factory(TransactionCheckBoxForm, extra=0)
        #initial_data = [{'value':False, 'object_id':t.id} for t in transactions]
        #formset = TransactionFormSet(request.POST, request.FILES, initial=initial_data)
        formset = TransactionFormSet(request.POST, request.FILES)

        if action and formset.is_valid():
            cleaned_data = formset.cleaned_data
            # Cleaned data is a list of dicts of the form:
            # {'object_id':X, 'value':False }
            # We need to perform the action on the objects whose values are True
            ids = [d['object_id'] for d in cleaned_data if d['value']]

            # NOTE: the following perform BULK operations, so they don't execute Transaction.save()
            if action == 'delete':
                Transaction.objects.filter(id__in=ids).delete()
            elif action == 'remove-pending':
                Transaction.objects.filter(id__in=ids).update(pending=False)

    return redirect(account)

@login_required
def transaction_detail(request, account_slug, transaction_id):
    """
    Show all the details associated with a single Transaction.
    """
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    transaction = get_object_or_404(Transaction, account=account, id=transaction_id)
    
    data = {'account':account, 'transaction': transaction}
    return render_to_response('coffers/transaction_detail.html', 
                              data,
                              context_instance=RequestContext(request))

