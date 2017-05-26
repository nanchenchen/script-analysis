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
        make_option('-t', '--type',
                    default='cosine',
                    dest='type',
                    help='Target similarity type'
        ),
        make_option('-T', '--threshold',
                    default=0.8,
                    dest='threshold',
                    help='Save diff content above a threshold'
        ),

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

        from pyanalysis.apps.enhance.models import SimilarityPair, ScriptDiff
        pairs = SimilarityPair.objects.filter(type=type, src_script__dataset_id=dataset_id, similarity__gte=threshold)


        bulk_diff = []
        for pair in pairs:
            diff_content = pair.get_diff()
            if diff_content.strip() == "":
                continue
            diff_obj = ScriptDiff(pair=pair, text=diff_content)
            bulk_diff.append(diff_obj)

            if (len(bulk_diff) % 100) == 0:
                ScriptDiff.objects.bulk_create(bulk_diff)
                bulk_diff = []

        ScriptDiff.objects.bulk_create(bulk_diff)