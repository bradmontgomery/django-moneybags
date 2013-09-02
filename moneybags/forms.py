from django import forms
from models import Account, Transaction, RecurringTransaction


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ('owner', 'slug', )


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ('account', 'updated_on')


class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = ('frequency_start_date', 'frequency', )


class TransactionCheckBoxForm(forms.Form):
    """ This is a form used to provide a general purpose ``checkbox`` widget
    for a ``Transaction``.
    """
    value = forms.BooleanField(required=False)
    object_id = forms.IntegerField(required=True, widget=forms.HiddenInput)


class TransactionReportForm(forms.Form):
    """This form lets us view ``Transactions`` matching certain criteria."""
    MATCHING_OPTIONS = [
        ('iexact', ''),
        ('startswith', 'Starts With'),
        ('endswith', 'Ends With'),
        ('exact', 'Exact'),
    ]
    description = forms.CharField(
        help_text="Search for a Transaction Description")
    description_match = forms.ChoiceField(choices=MATCHING_OPTIONS)
    from_date = forms.DateField(required=False,
        help_text="(optional) Match Transactions starting with this date. "
                  "Format: mm/dd/YYY")
    to_date = forms.DateField(required=False,
        help_text="(optional) Match Transactions up to this date. "
                  "Format: mm/dd/YYY")

    def get_matching_transactions(self):
        """Do the query to get matching Transactions. This should only be
        called after validation."""
        from_date = self.cleaned_data.get('from_date', None)
        to_date = self.cleaned_data.get('to_date', None)
        desc = self.cleaned_data['description']
        matching = self.cleaned_data['description_match']

        transactions = Transaction.objects.all()
        if from_date:
            transactions = transactions.filter(date__gte=from_date)
        if to_date:
            transactions = transactions.filter(date__lte=to_date)
        if matching == "startswith":
            transactions = transactions.filter(description__istartswith=desc)
        elif matching == "endswith":
            transactions = transactions.filter(date__iendswith=desc)
        elif matching == "exact":
            transactions = transactions.filter(date=desc)
        else:  # iexact
            transactions = transactions.filter(date__iexact=desc)
        return transactions


def modelform_handler(request, form_klass, instance=None, commit=True):
    """
    A convenience function to handle ModelForm creation and
    Validation in a View.

    Parameters:
    * ``request`` - the HttpRequest object
    * ``form_klass`` - a subclass of ModelForm
    * ``instance`` - an object that gets passed into the ``form_klass``
    * ``commit`` - True or False; this is passed into the
                   ``form_klass``'s ``save`` method.

    Returns a tuple: (``form``, ``object``) where ``form`` is
    and instance of ``form_klass`` and ``object`` is the result
    of calling ``form.save()`` or ``None``.

    """
    obj = None

    if request.method == "POST":
        if instance:
            form = form_klass(request.POST, instance=instance)
        else:
            form = form_klass(request.POST)

        if form.is_valid():
            obj = form.save(commit=commit)
    else:
        if instance:
            form = form_klass(instance=instance)
        else:
            form = form_klass()

    return (form, obj)
