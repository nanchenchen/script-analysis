from django.core.management.base import BaseCommand, make_option, CommandError
from time import time
import path
from django.db import transaction

class Command(BaseCommand):
    help = "Build dictionary for a dataset."
    args = '<dataset_id> [...]'

    def handle(self, dataset_id, **options):

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")


        from pyanalysis.apps.enhance.tasks import build_script_dictionary
        build_script_dictionary(dataset_id=dataset_id)


