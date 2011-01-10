import datetime
import os

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify

AMOUNT_MAX_DIGITS = 20
AMOUNT_DECIMAL_PLACES = 2

class Account(models.Model):
    """
    An account is an "container" for Transactions, and is "owned" by a ``User``.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def save(self, *args, **kwargs):
        """ Generate the slug from the name """
        self.slug = slugify(self.name)
        super(Account, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('coffers-account-detail', args=[self.slug,])

class Transaction(models.Model):
    """
    This class represents a monetary transaction.
    """
    TRANSACTION_TYPE = (
        (1, 'Credit'),
        (-1, 'Debit'),
    )
    date = models.DateField(help_text="The Date of this transaction")
    check_no = models.PositiveIntegerField(blank=True, null=True, help_text="Optional: Check Number")
    description = models.CharField(max_length=255, help_text="Description for this Transaction")
    amount = models.DecimalField(max_digits=AMOUNT_MAX_DIGITS, decimal_places=AMOUNT_DECIMAL_PLACES, help_text="Amount of this Transaction")
    recurring = models.BooleanField(blank=True, default=False, help_text="Is this a Recurring Transaction")
    pending = models.BooleanField(blank=True, default=True, help_text="Is this transaction still pending?")
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE)
    account = models.ForeignKey(Account)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s on %s: %s' % (self.description, self.date, self.amount)

    class Meta:
        ordering = ['-date', ]
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transaction'
    
    def get_absolute_url(self):
        return self.account.get_absolute_url()

    def save(self, *args, **kwargs):
        """ 
        Before saving an object, we set the sign of the amount based on the
        transaction type. We then create or update a RecurringTransaction 
        if neccessaryl
        """
        self.amount = self.amount * self.transaction_type 
        super(Transaction, self).save(*args, **kwargs)
        self._create_or_update_recurring_transaction()

    def _create_or_update_recurring_transaction(self):
        self._recurring_transaction_created = False  # NOTE: not sure about doing it this way... ?
        if self.recurring:
            desc_slug = slugify(self.description)
            try:
                rd = RecurringTransaction.objects.get(desc_slug=desc_slug, account=self.account)
            except RecurringTransaction.DoesNotExist:
                rd = RecurringTransaction(desc_slug=desc_slug, account=self.account)
                self._recurring_transaction_created = True # .....

            rd.description = self.description
            rd.amount = self.amount
            rd.last_paid_on = self.date
            rd.save()

    def is_credit(self):    
        return self.transaction_type > 0
    
    def abs_amount(self):
        return abs(self.amount)

class RecurringTransaction(models.Model):
    """
    This model provides a way to track recurring transactions. Note
    that the ``desc_slug`` and ``account`` fields are set as ``unique_together``.

    One instance of this model will represent the "last" time a 
    recurring transaction was made.
    
    """
    FREQUENCY_CHOICES = (
        ('d', 'Daily'),
        ('w', 'Weekly'),
        ('b', 'Bi-Weekly'),
        ('m', 'Monthly'),
        ('y', 'Yearly'),
        ('q', 'Quarterly'),
    )
    description = models.CharField(max_length=255)
    desc_slug = models.SlugField(max_length=255)
    amount = models.DecimalField(max_digits=AMOUNT_MAX_DIGITS, decimal_places=AMOUNT_DECIMAL_PLACES)
    account = models.ForeignKey(Account)
    last_paid_on = models.DateField()
    frequency = models.CharField(max_length=1, choices=FREQUENCY_CHOICES)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s: last paid on %s' % (self.description, self.last_paid_on)

    class Meta:
        ordering = ['-last_paid_on', 'account', 'description']
        unique_together = ['account', 'desc_slug']
   
    def get_absolute_url(self):
        return self.account.get_absolute_url()

    def save(self, *args, **kwargs):
        """
        Just ``slugify`` the Description.
        """
        self.desc_slug = slugify(self.description)
        super(RecurringTransaction, self).save(*args, **kwargs)
