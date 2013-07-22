from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView


# /new/
# /<account_slug>/update/
# /<account_slug>/new/
# /<account_slug>/transaction/<transaction_id>/
# /<account_slug>/recurring/<transaction_id>/
# /<account_slug>/<transaction_id>/
# /<account_slug>/
# /accounts/
# /saved/
# /

urlpatterns = patterns('moneybags.views',
    url(r'^new/$',
        'account_create',
        name='moneybags-account-create'),

    url(r'^accounts/$',
        'account_list',
        name='moneybags-account-list'),

    url(r'^(?P<account_slug>.*)/update/$',
        'account_update',
        name='moneybags-account-update'),

    url(r'^(?P<account_slug>.*)/new/$',
        'new_transaction',
        name='moneybags-new-transaction'),

    url(r'^(?P<account_slug>.*)/transaction/(?P<transaction_id>\d+)/$',
        'transaction_detail',
        name='moneybags-transaction-detail'),

    url(r'^(?P<account_slug>.*)/recurring/(?P<recurring_transaction_id>\d+)/$',
        'edit_recurring_transaction',
        name='moneybags-edit-recurring-transaction'),

    url(r'^(?P<account_slug>.*)/(?P<transaction_id>\d+)/$',
        'recurring_transaction',
        name='moneybags-recurring-transaction'),

    url(r'^(?P<account_slug>.*)/$',
        'account_detail',
        name='moneybags-account-detail'),
)

urlpatterns += patterns('',
    url(r'^saved/$',
        TemplateView.as_view(template_name='moneybags/saved.html'),
        name='moneybags-saved'
    ),
    url(r'^$',
        TemplateView.as_view(template_name='moneybags/default.html'),
        name='moneybags-default'
    ),
)
