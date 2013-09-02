from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView


# /new/
# /<account_slug>/update/
# /<account_slug>/new/
# /<account_slug>/report/
# /<account_slug>/transaction/<transaction_id>/
# /<account_slug>/recurring/<transaction_id>/
# /<account_slug>/<transaction_id>/
# /<account_slug>/
# /accounts/
# /saved/
# /

urlpatterns = patterns('moneybags.views',
    url(r'^new/$',
        'create_account',
        name='moneybags-create-account'),

    url(r'^accounts/$',
        'list_accounts',
        name='moneybags-list-accounts'),

    url(r'^(?P<account_slug>.*)/update/$',
        'update_transactions',
        name='moneybags-update-transactions'),

    url(r'^(?P<account_slug>.*)/new/$',
        'create_transaction',
        name='moneybags-create-transaction'),

    url(r'^(?P<account_slug>.*)/report/$',
        'transaction_report',
        name='moneybags-transaction-report'),

    url(r'^(?P<account_slug>.*)/transaction/(?P<transaction_id>\d+)/$',
        'detail_transaction',
        name='moneybags-detail-transaction'),

    url(r'^(?P<account_slug>.*)/recurring/(?P<recurring_transaction_id>\d+)/$',
        'update_recurring_transaction',
        name='moneybags-update-recurring-transaction'),

    url(r'^(?P<account_slug>.*)/(?P<transaction_id>\d+)/$',
        'recurring_transaction',
        name='moneybags-recurring-transaction'),

    url(r'^(?P<account_slug>.*)/$',
        'detail_account',
        name='moneybags-detail-account'),
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
