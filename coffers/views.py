from datetime import date, timedelta

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.db.models import Q
#from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from models import Credit, Debit, RecurringTransaction

@login_required
def default(request):
    """
    List "recent" debits, credits, and any "upcoming" recurring transactions
    """
    today = date.today()
    since = timedelta(days=-30) + today
    credits = Credit.objects.filter(date__gte=since, owner=request.user)
    debits = Debit.objects.filter(date__gte=since, owner=request.user)
    recurring_debits = RecurringTransaction.objects.filter(last_paid_on__lt=today)

    data = {'credits':credits, 'debits':debits, 
            'recurring_debits':recurring_debits,
            'today':today, 'since':since 
           }
    return render_to_response('coffers/default.html', 
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
