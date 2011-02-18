from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('coffers.views',
    url(r'^$', direct_to_template, {'template':'coffers/default.html'}, name='coffers-default'),
    url(r'^coffers/new/$', 'coffer_create', name='coffers-coffer-create'),
    url(r'^coffers/(?P<coffer_slug>.*)/update/$', 'coffer_update', name='coffers-coffer-update'),
    url(r'^coffers/(?P<coffer_slug>.*)/new/$', 'new_transaction', name='coffers-new-transaction'),
    url(r'^coffers/(?P<coffer_slug>.*)/transaction/(?P<transaction_id>\d+)/$', 'transaction_detail', name='coffers-transaction-detail'),
    url(r'^coffers/(?P<coffer_slug>.*)/recurring/(?P<recurring_transaction_id>\d+)/$', 'edit_recurring_transaction', name='coffers-edit-recurring-transaction'),
    url(r'^coffers/(?P<coffer_slug>.*)/(?P<transaction_id>\d+)/$', 'recurring_transaction', name='coffers-recurring-transaction'),
    url(r'^coffers/(?P<coffer_slug>.*)/$', 'coffer_detail', name='coffers-coffer-detail'),
    url(r'^coffers/$', 'coffer_list', name='coffers-coffer-list'),

    url(r'^saved/$', direct_to_template, {'template':'coffers/saved.html'}, name='coffers-saved'), 
)
