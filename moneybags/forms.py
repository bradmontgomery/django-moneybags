from django import forms
from models import Coffer, Transaction, RecurringTransaction

class CofferForm(forms.ModelForm):
    class Meta:
        model = Coffer
        exclude = ('owner', 'slug', )

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ('coffer', 'updated_on')

class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = ('frequency_start_date', 'frequency', )

class TransactionCheckBoxForm(forms.Form):
    """ 
    This is a form used to provide a general purpose ``checkbox`` widget for a ``Transaction``.
    """
    value = forms.BooleanField(required=False)
    object_id = forms.IntegerField(required=True, widget=forms.HiddenInput)

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
    object = None
    
    if request.method == "POST":
        if instance:
            form = form_klass(request.POST, instance=instance)
        else:
            form = form_klass(request.POST)
        
        if form.is_valid():
            object = form.save(commit=commit)
    else:
        if instance:
            form = form_klass(instance=instance)
        else:
            form = form_klass()
    
    return (form, object)
