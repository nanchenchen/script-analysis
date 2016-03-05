from django.core.management.base import BaseCommand, make_option, CommandError
import ast
from pyanalysis.apps.enhance.analyses import VariableCollector


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


#        from pyanalysis.apps.enhance.models import Dictionary
#        dictionary = Dictionary.objects.get(dataset_id=dataset_id)

        from pyanalysis.apps.corpus.models import Dataset
        dataset = Dataset.objects.get(id=dataset_id)

        src = dataset.scripts.all()[0].text
        tree = ast.parse(src)
        cc = VariableCollector()
        cc.visit(tree)
        print cc.variables

        import pdb
        pdb.set_trace()

