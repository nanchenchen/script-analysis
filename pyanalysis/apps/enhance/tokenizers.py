import ast
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


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


class TokenLoader(object):
    def __init__(self, scripts, *filters):
        """
        Filters is a list of objects which can be used like sets
        to determine if a word should be removed: if word in filter, then word will
        be ignored.
        """
        self.scripts = scripts
        self.filters = filters

    def __iter__(self):
        if self.scripts is None:
            raise RuntimeError("TokenLoader can only iterate if given scripts")

        for script in self.scripts:
            tokens = self.tokenize(script)
            if len(tokens) == 0:
                continue
            yield tokens

    def tokenize(self, obj):
        return map(lambda x: x.text, obj.tokens.all())


class CallTokenLoader(TokenLoader):

    def tokenize(self, obj):
        src = obj.text
        try:
            tree = ast.parse(src)
        except SyntaxError:
            logger.info("Syntax Error")
            return []
        except:
            import traceback
            traceback.print_exc()
            return []

        cc = CallCollector()
        cc.visit(tree)
        results = filter(lambda x: x is not None, cc.calls)
        for f in self.filters:
            results = filter(lambda x: x not in f, results)

        return results


class DiffTokenLoader(TokenLoader):

    def tokenize(self, obj):
        src = obj.text
        lines = src.split('\n')

        results = []

        for line in lines[4:]:
            if line.startswith('-') or line.startswith('+'):
                results.append(line[1:])

        return results
