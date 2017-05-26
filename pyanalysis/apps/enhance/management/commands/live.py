from django.core.management.base import BaseCommand, make_option, CommandError
import ast
import pyanalysis.apps.corpus.models as corpus_models
import pyanalysis.apps.enhance.models as enhance_models


class Command(BaseCommand):
    help = "Live commands with dictionary."
    args = '<dataset_id> [...]'

    def handle(self, dataset_id, **options):

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        dataset = corpus_models.Dataset.objects.get(dataset_id=dataset_id)

        scripts = dataset.scripts.all()


        import pdb
        pdb.set_trace()

