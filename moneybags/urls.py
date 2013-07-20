from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('moneybags.views',
    url(r'^$', direct_to_template, {'template':'moneybags/default.html'}, name='moneybags-default'),
    url(r'^moneybags/new/$', 'coffer_create', name='moneybags-coffer-create'),
    url(r'^moneybags/(?P<coffer_slug>.*)/update/$', 'coffer_update', name='moneybags-coffer-update'),
    url(r'^moneybags/(?P<coffer_slug>.*)/new/$', 'new_transaction', name='moneybags-new-transaction'),
    url(r'^moneybags/(?P<coffer_slug>.*)/transaction/(?P<transaction_id>\d+)/$', 'transaction_detail', name='moneybags-transaction-detail'),
    url(r'^moneybags/(?P<coffer_slug>.*)/recurring/(?P<recurring_transaction_id>\d+)/$', 'edit_recurring_transaction', name='moneybags-edit-recurring-transaction'),
    url(r'^moneybags/(?P<coffer_slug>.*)/(?P<transaction_id>\d+)/$', 'recurring_transaction', name='moneybags-recurring-transaction'),
    url(r'^moneybags/(?P<coffer_slug>.*)/$', 'coffer_detail', name='moneybags-coffer-detail'),
    url(r'^moneybags/$', 'coffer_list', name='moneybags-coffer-list'),

    url(r'^saved/$', direct_to_template, {'template':'moneybags/saved.html'}, name='moneybags-saved'), 
)
