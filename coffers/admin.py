from django.contrib import admin
from coffers import models 

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner', )
    search_fields = ('name', 'owner__username', 'owner__first_name', 'owner__last_name',)
    prepopulated_fields = {'slug': ('name',)}

class TransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('description', 'amount', 'date', 'recurring', 'pending', 'transaction_type') 
    list_filter = ('recurring', 'pending')
    search_fields = ('description', 'account__name')

class RecurringTransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'last_paid_on'
    list_display = ('description', 'last_paid_on', 'frequency', 'desc_slug', )
    search_fields = ('description', )

admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.RecurringTransaction, RecurringTransactionAdmin)
