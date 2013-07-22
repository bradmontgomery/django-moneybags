from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from moneybags.models import Account
from moneybags import utils

User = get_user_model()


class Command(BaseCommand):
    args = "<username> <account_slug> <path_to_csv_file>"
    help = """This command will load transactions from a CSV file.

    You must provide a username and an Account slug.

    Example Usage:

        python manage.py load_transactions_from_csv
            jdoe
            personal-checking
            /home/users/jdoe/checking.csv

    """

    def __init__(self, *args, **kwargs):
        """Initialize some attributes."""
        super(Command, self).__init__(*args, **kwargs)
        self.username = None
        self.account_slug = None
        self.csv_file = None

    def _parse_args(self, args):
        """Unpack the arguments, storing values as attributes."""
        if len(args) == 3:
            self.username, self.account_slug, self.csv_file = args
        else:
            raise CommandError("This command requires exactly 3 arguments.")

    def _get_user(self):
        try:
            return User.objects.get(username=self.username)
        except User.DoesNotExist:
            msg = "Could Not find User: '{0}'".format(self.username)
            raise CommandError(msg)

    def _get_account(self):
        user = self._get_user()
        try:
            return Account.objects.get(owner=user, slug=self.account_slug)
        except Account.DoesNotExist:
            msg = "Could Not find Account: '{0}'".format(self.account_slug)
            raise CommandError(msg)

    def handle(self, *args, **options):
        self._parse_args(args)
        account = self._get_account()

        transactions = utils.load_csv_data(self.csv_file)
        utils.create_transactions(account, transactions, verbose=True)
        self.stdout.write("\nDone!\n")
