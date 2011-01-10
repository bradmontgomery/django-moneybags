from datetime import date, timedelta

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.db.models import Q
#from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from models import Account, Credit, Debit, RecurringTransaction
from forms import AccountForm, modelform_handler

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

    today = date.today()
    since = timedelta(days=-30) + today
    credits = Credit.objects.filter(date__gte=since, account=account).order_by('-date', 'id')
    debits = Debit.objects.filter(date__gte=since, account=account).order_by('-date', 'id')
    recurring_transactions = RecurringTransaction.objects.filter(last_paid_on__lt=today)

    total_credits = sum([t.amount for t in credits])
    total_debits = sum([t.amount for t in debits])
    balance = total_credits - total_debits
    
    # List both Credits & Debits in a single data structure organized by date
    transactions = []
    for t in list(credits) + list(debits):
        trans = {'recurring':False, 'credit': False, 'object':None, 'date':None}
        trans['object'] = t
        trans['date'] = t.date
        if t.__class__ == Credit:
            trans['credit'] = True
        transactions.append(trans)

    
    data = {'account':account, 'transactions': transactions,
            'recurring_transactions':recurring_transactions,
            'today':today, 'since':since, 'balance':balance
           }
    return render_to_response('coffers/account_detail.html', 
                              data,
                              context_instance=RequestContext(request))

@login_required
def save_stuff(request, category_id=0, ticket_id=None):
    #if request.method == 'POST':
    #    form = SOMEForm(request.POST)
    #    if form.is_valid():
    #        # do stuff
    #else:
    #    form = TicketForm()
    #
    return render_to_response('coffers/saved.html', 
                               locals(), 
                               context_instance=RequestContext(request))
