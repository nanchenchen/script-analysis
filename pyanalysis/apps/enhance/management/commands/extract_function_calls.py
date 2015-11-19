from django.core.management.base import BaseCommand, make_option, CommandError
from time import time
import path
from django.db import transaction
import ast


import logging
logger = logging.getLogger(__name__)


class CallCollector(ast.NodeVisitor):
    '''
        A class for visiting nodes, copied and modified from
        http://stackoverflow.com/questions/26014404/how-to-extract-functions-used-in-a-python-code-file
    '''
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
    help = "Extract function calls."
    args = '<dataset_id>'

    def handle(self, dataset_id, **options):

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        from pyanalysis.apps.corpus.models import Dataset, FunctionCall
        dataset = Dataset.objects.get(id=dataset_id)

        with transaction.atomic(savepoint=False):
            scripts = dataset.scripts.all()
            for idx, script in enumerate(scripts):
                logger.info("Processing %d/%d scripts: %s" %(idx + 1, len(scripts), script.name))
                src = script.contents
                try:
                    tree = ast.parse(src)
                except SyntaxError:
                    logger.info("Syntax Error")
                    continue

                cc = CallCollector()
                cc.visit(tree)
                calls = map(lambda x: FunctionCall(script=script, name=x), cc.calls)
                FunctionCall.objects.bulk_create(calls)

                logger.info("Found %d function calls" %(len(calls)) )





