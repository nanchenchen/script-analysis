from django.core.management.base import BaseCommand, make_option, CommandError
from time import time
import path
from django.db import transaction
import ast

class CallCollector(ast.NodeVisitor):
    def __init__(self):
        self.calls = []
        self.current = None

    def visit_Call(self, node):
        # new call, trace the function expression
        self.current = ''
        self.visit(node.func)
        self.calls.append(self.current)
        self.current = None

    def generic_visit(self, node):
        if self.current is not None:
            print "warning: {} node in function expression not supported".format(
                node.__class__.__name__)
        super(CallCollector, self).generic_visit(node)

    # record the func expression
    def visit_Name(self, node):
        if self.current is None:
            return
        self.current += node.id

    def visit_Attribute(self, node):
        if self.current is None:
            self.generic_visit(node)
        self.visit(node.value)

        if self.current is not None:
            self.current += '.' + node.attr



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

        src = dataset.scripts.all()[0].contents
        tree = ast.parse(src)
        cc = CallCollector()
        cc.visit(tree)
        print cc.calls

        import pdb
        pdb.set_trace()

