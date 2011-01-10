from datetime import date, timedelta

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.db.models import Q
#from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from models import Account, Transaction, RecurringTransaction
from forms import AccountForm, TransactionForm, modelform_handler

@login_required
def new_transaction(request, account_slug):
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    form, object = modelform_handler(request, TransactionForm, commit=False)
    if object:
        object.account = account
        #TODO: if this is recurring, redirect to the recurring info form

        object.save()
        return redirect(object)

    data = {'account':account, 'form':form, 'object':object }
    return render_to_response('coffers/new_transaction.html', 
                               data,
                               context_instance=RequestContext(request))

@login_required
def recurring_transaction(request, object_id):
    account = get_object_or_404(Account, slug=account_slug, owner=request.user)
    recurring_transaction = get_object_or_404(RecurringTransaction, account=account)

    #TODO: finish this, make sure correct info is saved, then redirect to Account details.
    #form, object = modelform_handler(request, RecurringTransactionForm, commit=False)
    #if object:
    #
    #    object.save()
    #    return redirect(object)

    #data = {'account':account, 'form':form, 'object':object }
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
    recurring_transactions = RecurringTransaction.objects.filter(last_paid_on__lt=today)
    
    data = {'account':account, 'transactions': transactions,
            'recurring_transactions':recurring_transactions,
            'today':today, 'since':since, 'balance':balance
           }
    return render_to_response('coffers/account_detail.html', 
                              data,
                              context_instance=RequestContext(request))
