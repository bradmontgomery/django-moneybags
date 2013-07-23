import datetime

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

from .settings import (
    AMOUNT_DECIMAL_PLACES,
    AMOUNT_MAX_DIGITS,
    TRANSACTION_TYPE_DEBIT,
    TRANSACTION_TYPE_CREDIT,
)

User = get_user_model()


class Account(models.Model):
    """A named container for Transactions, and is owned by a ``User``."""
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
        return reverse('moneybags-detail-account', args=[self.slug])

    def _get_debits(self):
        """return the sum of all debits for this account"""
        debits = self.transaction_set.filter(transaction_type=-1)
        debits = debits.values_list('amount', flat=True)
        return sum(list(debits))

    def _get_credits(self):
        """ return the sum of all credits for this account"""
        credits = self.transaction_set.filter(transaction_type=1)
        credits = credits.values_list('amount', flat=True)
        return sum(list(credits))

    def get_balance(self):
        credits = self._get_credits()
        debits = self._get_debits()
        return credits - debits


class TransactionManager(models.Manager):

    def debits(self):
        return self.filter(transaction_type=-1)

    def credits(self):
        return self.filter(transaction_type=1)

    # TODO: put in aggregate functions here that accept account as input, and
    #       give us the balance, total debits, total credits?


class Transaction(models.Model):
    """This class represents a monetary transaction."""
    TRANSACTION_TYPE = (
        (TRANSACTION_TYPE_CREDIT, 'Credit'),
        (TRANSACTION_TYPE_DEBIT, 'Debit'),
    )
    account = models.ForeignKey(Account)
    date = models.DateField(help_text="The Date of this transaction")
    check_no = models.PositiveIntegerField(blank=True, null=True,
        help_text="Optional: Check Number")
    description = models.CharField(max_length=255,
        help_text="Description for this Transaction")
    amount = models.DecimalField(max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        help_text="Amount of this Transaction")
    recurring = models.BooleanField(blank=True, default=False,
        help_text="Is this a Recurring Transaction")
    pending = models.BooleanField(blank=True, default=True,
        help_text="Is this transaction still pending?")
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE,
        help_text="The Type of Transaction")
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{0} on {1}: {2}".format(
            self.description,
            self.date,
            self.amount
        )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transaction'

    def get_absolute_url(self):
        args = [self.account.slug, self.id]
        return reverse('moneybags-detail-transaction', args=args)

    def get_recurring_transaction_url(self):
        args = [self.account.slug, self.id]
        return reverse('moneybags-recurring-transaction', args=args)

    def save(self, *args, **kwargs):
        """
        Before saving an object, we set the sign of the amount based on the
        transaction type. We then create or update a RecurringTransaction
        if neccessary.
        """
        super(Transaction, self).save(*args, **kwargs)
        self._create_or_update_recurring_transaction()

    def _create_or_update_recurring_transaction(self):
        """
        If this transaction is recurring, this method will fetch the
        corresponding ``RecurringTransaction`` object, if it exists. If the
        ``RecurringTrasaction`` object does not exist, it will be created.

        In either case, the ``RecurringTransaction`` instance is updated with
        values from this ``Transaction``.

        This method returns a tuple containing 2 objects:

        1. An instance of ``RecurringTransaction``
        2. A boolean value indicating whether or not the object was created
        """
        if self.recurring:
            desc_slug = slugify(self.description)
            try:
                rt = RecurringTransaction.objects.get(
                    desc_slug=desc_slug,
                    account=self.account,
                    transaction_type=self.transaction_type
                )
            except RecurringTransaction.DoesNotExist:
                rt = RecurringTransaction(
                    desc_slug=desc_slug,
                    account=self.account,
                    transaction_type=self.transaction_type
                )
                rt.frequency_start_date = self.date

            rt.description = self.description
            rt.amount = self.amount
            rt.last_transaction_date = self.date
            rt.save()

    def is_credit(self):
        return self.transaction_type > 0

    def abs_amount(self):
        return abs(self.amount)

    def get_recurring_transaction(self):
        rt = None
        if self.recurring:
            try:
                rt = RecurringTransaction.objects.get(
                    desc_slug=slugify(self.description),
                    account=self.account,
                    transaction_type=self.transaction_type
                )
            except RecurringTransaction.DoesNotExist:
                # Ugh... create it?
                rt = RecurringTransaction(
                    desc_slug=slugify(self.description),
                    account=self.account,
                    transaction_type=self.transaction_type
                )
                rt.description = self.description
                rt.amount = self.amount
                rt.last_transaction_date = self.date
                rt.frequency_start_date = self.date
                rt.save()

        return rt

    def get_similar_transactions(self):
        transactions = Transaction.objects.filter(
            description=self.description,
            transaction_type=self.transaction_type,
            account=self.account
        )
        transactions = transactions.exclude(id=self.id).order_by('-date')
        return transactions

    admin_objects = models.Manager()
    objects = TransactionManager()


class RecurringTransactionManager(models.Manager):
    def due_today(self):
        return self.filter(due_date=datetime.date.today())


class RecurringTransaction(models.Model):
    """This model provides a way to track recurring transactions. Note
    that the ``desc_slug`` and ``account`` fields are set as
    ``unique_together``.

    One instance of this model will represent the "last" time a recurring
    transaction was made.

    """
    FREQUENCY_CHOICES = (
        ('d', 'Daily'),
        ('w', 'Weekly'),
        ('b', 'Bi-Weekly'),
        ('m', 'Monthly'),
        ('y', 'Yearly'),
        ('q', 'Quarterly'),
    )
    description = models.CharField(max_length=255,
        help_text="This should match the description from the Transaction")
    desc_slug = models.SlugField(max_length=255,
        help_text="A sluggified version of the description")
    amount = models.DecimalField(max_digits=AMOUNT_MAX_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        help_text="Amount to be paid")
    account = models.ForeignKey(Account,
        help_text="The Account in which this belongs")
    frequency = models.CharField(max_length=1, choices=FREQUENCY_CHOICES)
    frequency_start_date = models.DateField(
        help_text="The date from which the frequency should be calculated")
    last_transaction_date = models.DateField(
        help_text="The date on which the last transaction occurred")
    transaction_type = models.IntegerField(
        choices=Transaction.TRANSACTION_TYPE,
        help_text="The Type of Transaction")
    due_date = models.DateField(help_text="Automatically Generated from the "
        "Frequency and Frequency Start Date")
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}: {1} - last transaction date {2}".format(
            self.account.name,
            self.description,
            self.last_transaction_date
        )

    class Meta:
        ordering = ['-last_transaction_date', 'account', 'description']
        unique_together = ['account', 'desc_slug']

    def get_absolute_url(self):
        return self.account.get_absolute_url()

    def get_edit_url(self):
        args = [self.account.slug, self.id]
        return reverse('moneybags-update-recurring-transaction', args=args)

    def save(self, *args, **kwargs):
        """Just ``slugify`` the Description."""
        self.desc_slug = slugify(self.description)
        self.due_date = self.get_due_date() or self.frequency_start_date or \
            self.last_transaction_date
        super(RecurringTransaction, self).save(*args, **kwargs)

    def get_type(self):
        """credit if amount > 0, debit otherwise """
        if self.transaction_type > 0:
            return 'credit'
        return 'debit'

    def get_due_date(self):
        """ Calculate the due date for this recurring transaction """
        new_date = None
        prev_date = max(self.frequency_start_date, self.last_transaction_date)
        if self.frequency == 'd':
            new_date = prev_date + datetime.timedelta(days=1)
        elif self.frequency == 'w':
            new_date = prev_date + datetime.timedelta(days=7)
        elif self.frequency == 'b':
            new_date = prev_date + datetime.timedelta(days=14)
        elif self.frequency == 'm':
            new_date = prev_date + datetime.timedelta(365 / 12)
        elif self.frequency == 'y':
            new_date = prev_date + datetime.timedelta(days=365)
        elif self.frequency == 'q':
            new_date = prev_date + datetime.timedelta(days=90)

        return new_date

    objects = RecurringTransactionManager()


def create_transactions_due_today():
    """Create ``Transaction`` objects for all of the ``RecurringTransaction``'s
    that are due today. This should be run as a a scheduled task.
    """
    for rt in RecurringTransaction.objects.due_today():
        # Make sure it doesn't already exist!
        transactions = Transaction.objects.filter(date=rt.due_date,
            description=rt.description,
            amount=rt.amount,
            recurring=True,
            account=rt.account,
            transaction_type=rt.transaction_type
        )
        if transactions.count() == 0:
            new_trans = Transaction(date=rt.due_date, account=rt.account)
            new_trans.description = rt.description
            new_trans.amount = rt.amount
            new_trans.recurring = True
            new_trans.pending = True
            new_trans.transaction_type = rt.transaction_type
            new_trans.save()
