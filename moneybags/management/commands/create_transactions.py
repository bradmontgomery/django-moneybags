from django.core.management.base import NoArgsCommand
from moneybags.models import create_transactions_due_today

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        create_transactions_due_today()
