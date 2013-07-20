from django.contrib import admin
from moneybags import models 

class CofferAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'owner', )
    search_fields = ('name', 'owner__username', 'owner__first_name', 'owner__last_name',)
    prepopulated_fields = {'slug': ('name',)}

class TransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('description', 'amount', 'coffer', 'date', 'recurring', 'pending', 'transaction_type') 
    list_filter = ('recurring', 'pending')
    search_fields = ('description', 'coffer__name')

class RecurringTransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'last_transaction_date'
    list_display = ('due_date', 'coffer', 'description', 'desc_slug', 'frequency', 'frequency_start_date', 'last_transaction_date', )
    search_fields = ('description', 'coffer__name')

admin.site.register(models.Coffer, CofferAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.RecurringTransaction, RecurringTransactionAdmin)
