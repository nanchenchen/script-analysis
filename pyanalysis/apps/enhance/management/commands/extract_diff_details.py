from django.core.management.base import BaseCommand, make_option, CommandError
from time import time
import path
from django.db import transaction

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run gensim operations."
    args = '<dataset_id>'
    option_list = BaseCommand.option_list + (


    )

    def handle(self, dataset_id, **options):

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        type = options.get('type')
        threshold = options.get('threshold')

        from pyanalysis.apps.enhance.models import ScriptDiff
        diffs = ScriptDiff.objects.all()[0]

        # Step 1: Extract + and - lines
        diff_text = diffs.text
        diff_lines = diff_text.split('\n')[3:] # skip first few lines
        diff_lines_plus = filter(lambda x: x.startswith('+'), diff_lines)
        diff_lines_minus = filter(lambda x: x.startswith('-'), diff_lines)
        diff_lines_plus = [x[1:] for x in diff_lines_plus]   # remove + sign
        diff_lines_minus = [x[1:] for x in diff_lines_minus] # remove - sign
        print diff_lines_plus
        print diff_lines_minus



        # bulk_diff = []
        # for pair in pairs:
        #     diff_content = pair.get_diff()
        #     if diff_content.strip() == "":
        #         continue
        #     diff_obj = ScriptDiff(pair=pair, text=diff_content)
        #     bulk_diff.append(diff_obj)
        #
        #     if (len(bulk_diff) % 100) == 0:
        #         ScriptDiff.objects.bulk_create(bulk_diff)
        #         bulk_diff = []
        #
        # ScriptDiff.objects.bulk_create(bulk_diff)