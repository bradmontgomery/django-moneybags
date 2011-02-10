from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('coffers.views',
    url(r'^$', direct_to_template, {'template':'coffers/default.html'}, name='coffers-default'),
    url(r'^accounts/new/$', 'account_create', name='coffers-accounts-create'),
    url(r'^accounts/(?P<account_slug>.*)/update/$', 'account_update', name='coffers-account-update'),
    url(r'^accounts/(?P<account_slug>.*)/new/$', 'new_transaction', name='coffers-new-transaction'),
    url(r'^accounts/(?P<account_slug>.*)/transaction/(?P<transaction_id>\d+)/$', 'transaction_detail', name='coffers-transaction-detail'),
    url(r'^accounts/(?P<account_slug>.*)/recurring/(?P<recurring_transaction_id>\d+)/$', 'edit_recurring_transaction', name='coffers-edit-recurring-transaction'),
    url(r'^accounts/(?P<account_slug>.*)/(?P<transaction_id>\d+)/$', 'recurring_transaction', name='coffers-recurring-transaction'),
    url(r'^accounts/(?P<account_slug>.*)/$', 'account_detail', name='coffers-account-detail'),
    url(r'^accounts/$', 'account_list', name='coffers-account-list'),

    url(r'^saved/$', direct_to_template, {'template':'coffers/saved.html'}, name='coffers-saved'), 
)
