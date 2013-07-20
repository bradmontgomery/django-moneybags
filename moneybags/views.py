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

from models import Coffer, Transaction, RecurringTransaction
from forms import CofferForm, TransactionForm, TransactionCheckBoxForm, RecurringTransactionForm, modelform_handler

@login_required
def new_transaction(request, coffer_slug):
    coffer = get_object_or_404(Coffer, slug=coffer_slug, owner=request.user)
    form, object = modelform_handler(request, TransactionForm, commit=False)
    if object:
        object.coffer = coffer
        object.save()
        if object.recurring:
            return redirect(object.get_recurring_transaction_url())
        return redirect(object.coffer) # coffer detail

    data = {'coffer':coffer, 'form':form, 'object':object }
    return render_to_response('coffers/new_transaction.html', 
                               data,
                               context_instance=RequestContext(request))

@login_required
def recurring_transaction(request, coffer_slug, transaction_id):
    coffer = get_object_or_404(Coffer, slug=coffer_slug, owner=request.user)
    transaction = get_object_or_404(Transaction, pk=transaction_id, coffer=coffer)
    recurring_transaction = transaction.get_recurring_transaction()

    if recurring_transaction:
        form, object = modelform_handler(request, RecurringTransactionForm, instance=recurring_transaction, commit=True)
        if object:
            return redirect(object)

        data = {'coffer':coffer, 'form':form, 'transaction':transaction  }
    else:
        raise Http404

    return render_to_response('coffers/recurring_transaction.html', 
                               data,
                               context_instance=RequestContext(request))

@login_required
def edit_recurring_transaction(request, coffer_slug, recurring_transaction_id):
    coffer = get_object_or_404(Coffer, slug=coffer_slug, owner=request.user)
    recurring_transaction = get_object_or_404(RecurringTransaction, pk=recurring_transaction_id, coffer=coffer)

    if recurring_transaction:
        form, object = modelform_handler(request, RecurringTransactionForm, instance=recurring_transaction, commit=True)
        if object:
            return redirect(object)

        data = {'coffer':coffer, 'form':form, 'recurring_transaction':recurring_transaction}
    else:
        raise Http404

    return render_to_response('coffers/edit_recurring_transaction.html', 
                               data,
                               context_instance=RequestContext(request))

@login_required
def coffer_list(request):
    coffers = Coffer.objects.filter(owner=request.user)
    return render_to_response('coffers/coffer_list.html', 
                               {'coffers':coffers}, 
                               context_instance=RequestContext(request))

@login_required
def coffer_create(request):
    """ create a new coffer """ 
    form, object = modelform_handler(request, CofferForm, commit=False)
    if object:
        object.owner = request.user
        object.save()
        return redirect(object)
    return render_to_response('coffers/coffer_create.html', 
                               {'form':form}, 
                               context_instance=RequestContext(request))

@login_required
def coffer_detail(request, coffer_slug):
    """
    List "recent" debits, credits, and any "upcoming" recurring transactions
    """
    coffer = get_object_or_404(Coffer, slug=coffer_slug, owner=request.user)
    # get the balance of all Transactions.
    #debits = sum(list(Transaction.objects.debits().filter(coffer=coffer).values_list('amount', flat=True)))
    #credits = sum(list(Transaction.objects.credits().filter(coffer=coffer).values_list('amount', flat=True)))
    balance = coffer.get_balance()
    
    # Display the 30 days worth of transactions.
    today = date.today()
    since = timedelta(days=-30) + today
    
    ##TODO: 
    ## for recurring transactions to automatically get dumped into the "Transaction" list, we've got to run the
    ## ``coffers_create_transactions_due_today`` Management command.  Now, that'll create a Transaction based on RecurringTranscations,
    ## BUT, the recurringTransaction will still have the wrong date. Either the model, or the managment command needs to 
    ## update it's due date, 
    transactions = Transaction.objects.filter(date__gte=since, coffer=coffer).order_by('-date', 'id')
    recurring_transactions = RecurringTransaction.objects.filter(due_date__gte=today, coffer=coffer).order_by('-due_date', 'id')
    
    # Create a FormSet using a TransactionCheckBoxForm for each Transaction listed.
    TransactionFormSet = formset_factory(TransactionCheckBoxForm, extra=0)
    initial_data = [{'value':False, 'object_id':t.id} for t in transactions]
    formset = TransactionFormSet(initial=initial_data)

    data = {'coffer':coffer, 'transactions': transactions,
            'recurring_transactions':recurring_transactions,
            'today':today, 'since':since, 'balance':balance,
            'overdrawn': not balance > 0, 'formset':formset, 
           }
    return render_to_response('coffers/coffer_detail.html', 
                              data,
                              context_instance=RequestContext(request))

@login_required
def coffer_update(request, coffer_slug):
    """ 
    Handle POST from coffer_detail, and update selected transactions:
    
    - delete
    - set as pending/not pending
    
    Then redirect to coffer detail 
    """ 
    coffer = get_object_or_404(Coffer, slug=coffer_slug, owner=request.user)
   
    cleaned_data = None
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action', None)

        #TODO: the next 3 lines are the same as in coffer_detail
        today = date.today()
        since = timedelta(days=-30) + today
        transactions = Transaction.objects.filter(date__gte=since, coffer=coffer).order_by('-date', 'id')

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

    return redirect(coffer)

@login_required
def transaction_detail(request, coffer_slug, transaction_id):
    """
    Show all the details associated with a single Transaction.
    """
    coffer = get_object_or_404(Coffer, slug=coffer_slug, owner=request.user)
    transaction = get_object_or_404(Transaction, coffer=coffer, id=transaction_id)
   
    similar_transactions = transaction.get_similar_transactions()
    data = {'coffer':coffer, 'transaction': transaction, 'similar_transactions':similar_transactions}
    return render_to_response('coffers/transaction_detail.html', 
                              data,
                              context_instance=RequestContext(request))

