from django.contrib import admin
from moneybags import models


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner', )
    search_fields = (
        'name', 'owner__username', 'owner__first_name', 'owner__last_name'
    )
    prepopulated_fields = {'slug': ('name',)}


class TransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = (
        'description', 'amount', 'account', 'date', 'recurring', 'pending',
        'transaction_type'
    )
    list_filter = ('recurring', 'pending')
    search_fields = ('description', 'account__name')


class RecurringTransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'last_transaction_date'
    list_display = (
        'due_date', 'account', 'description', 'desc_slug', 'frequency',
        'frequency_start_date', 'last_transaction_date'
    )
    search_fields = ('description', 'account__name')


admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.RecurringTransaction, RecurringTransactionAdmin)
