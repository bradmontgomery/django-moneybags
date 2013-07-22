from django.conf import settings


# Constant values for debit/credit transaction types. This is used in the
# Transaction.TRANSACTION_TYPE choice.
TRANSACTION_TYPE_DEBIT = getattr(settings,
    'MONEYBAGS_TRANSACTION_TYPE_DEBIT', -1)
TRANSACTION_TYPE_CREDIT = getattr(settings,
    'MONEYBAGS_TRANSACTION_TYPE_CREDIT', 1)

# Decimal Configuration for money values
AMOUNT_DECIMAL_PLACES = getattr(settings,
    'MONEYBAGS_AMOUNT_DECIMAL_PLACES', 2)
AMOUNT_MAX_DIGITS = getattr(settings,
    'MONEYBAGS_AMOUNT_MAX_DIGITS', 20)
