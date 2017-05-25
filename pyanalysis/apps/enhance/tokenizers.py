import numpy as np
from StringIO import StringIO
import tokenize
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

    def tokenize_line(self, line):

        tokens = tokenize.generate_tokens(StringIO(line).readline)
        tokens_list = []
        for token in tokens:
            type = tokenize.tok_name[token[0]]
            text = token[1]
            tokens_list.append((type, text))
        return tokens_list


    def filter_out_token(self, seq):
        remove_types = ['OP', #'COMMENT',
                        'ENDMARKER', 'NL']
        return filter(lambda (token_type, token_text): token_type not in remove_types, seq)

    def editing_dist(self, seq1, seq2, mode='dist'):
        seq1 = self.filter_out_token(seq1)
        seq2 = self.filter_out_token(seq2)

        len1 = len(seq1)
        len2 = len(seq2)
        if len1 == 0 and len2 == 0:
            if mode == 'dist':
                return 0
            elif mode == 'diff':
                return []
        dp = np.zeros((len1 + 1, len2 + 1))

        # initialize empty string's editing dist
        for idx1, seq1_ele in enumerate(seq1):
            dp[idx1 + 1][0] = idx1 + 1

        for idx2, seq2_ele in enumerate(seq2):
            dp[0][idx2 + 1] = idx2 + 1

        for idx1, seq1_ele in enumerate(seq1):
            for idx2, seq2_ele in enumerate(seq2):
                if seq1_ele == seq2_ele:
                    dp[idx1 + 1][idx2 + 1] = dp[idx1][idx2]
                else:
                    dp[idx1 + 1][idx2 + 1] = min(dp[idx1 + 1][idx2], dp[idx1][idx2 + 1]) + 1
        if mode == 'dist':
            return dp[len1][len2] / (len1 + len2)
        elif mode == 'diff':
            diff_tokens = []
            i = len1
            j = len2
            while i > 0 and j > 0:
                if seq1[i - 1] == seq2[j - 1]:
                    i -= 1
                    j -= 1
                elif dp[i - 1][j] <= dp[i][j - 1]:
                    diff_tokens = [seq1[i - 1]] + diff_tokens
                    i -= 1
                elif dp[i - 1][j] > dp[i][j - 1]:
                    diff_tokens = [seq2[j - 1]] + diff_tokens
                    j -= 1
            return diff_tokens

    def line_matching_by_lcs(self, list1, list2, matching_threshold=0.5):

        len1 = len(list1)
        len2 = len(list2)
        dp = np.zeros((len1 + 1, len2 + 1))

        dist = np.zeros((len1, len2)) + float('inf')
        for i in range(len1):
            for j in range(len2):
                dist[i][j] = self.editing_dist(list1[i], list2[j])

        # import pprint
        # pprint.pprint(dist)

        for idx1, list1_ele in enumerate(list1):
            for idx2, list2_ele in enumerate(list2):
                if dist[idx1][idx2] < matching_threshold:
                    dp[idx1 + 1][idx2 + 1] = dp[idx1][idx2] + 1
                else:
                    dp[idx1 + 1][idx2 + 1] = max(dp[idx1 + 1][idx2], dp[idx1][idx2 + 1])

        #pprint.pprint(dp)


        i = len1
        j = len2
        matching_items = []
        while i > 0 and j > 0:
            if dist[i - 1][j - 1] < matching_threshold:
                matching_items = [(i - 1, j - 1)] + matching_items
                i -= 1
                j -= 1
            elif dp[i - 1][j] > dp[i][j - 1]:
                matching_items = [(i - 1, None)] + matching_items
                i -= 1
            else:
                matching_items = [(None, j - 1)] + matching_items
                j -= 1

        return matching_items

    def extract_diff_tokens(self, script_diff):
        #print "Script diff %d" %(idx)
        # Step 1: Extract + and - lines
        diff_text = script_diff.text
        diff_lines = diff_text.split('\n')[3:] # skip first few lines
        diff_lines_plus = filter(lambda x: x.startswith('+'), diff_lines)
        diff_lines_minus = filter(lambda x: x.startswith('-'), diff_lines)
        diff_lines_plus = [x[1:] for x in diff_lines_plus]   # remove + sign
        diff_lines_minus = [x[1:] for x in diff_lines_minus] # remove - sign

        # Step 1.5: Tokenize
        diff_lines_plus_t = [self.tokenize_line(line) for line in diff_lines_plus]   # tokenize
        diff_lines_minus_t = [self.tokenize_line(line) for line in diff_lines_minus]   # tokenize
        #print diff_lines_plus_t
        #print diff_lines_minus_t

        diff_tokens = []
        matching_items = self.line_matching_by_lcs(diff_lines_plus_t, diff_lines_minus_t)
        for (i, j) in matching_items:
            if i is not None and j is not None:
                # print "(%2d, %2d): %s\t|\t%s" %(i, j, diff_lines_plus[i], diff_lines_minus[j])
                diff_tokens += self.editing_dist(diff_lines_plus_t[i], diff_lines_minus_t[j], mode='diff')
            elif i is None and j is not None:
                # print "(  , %2d): --------\t|\t%s" %(j,  diff_lines_minus[j])
                diff_tokens += self.filter_out_token(diff_lines_minus_t[j])
            elif i is not None and j is None:
                # print "(%2d,   ): %s\t|\t--------" %(i,  diff_lines_plus[i])
                diff_tokens += self.filter_out_token(diff_lines_plus_t[i])


        # diff_tokens = map(lambda (token_type, text): token_type + '__' + text, diff_tokens)
        diff_tokens = map(lambda (token_type, text): text, diff_tokens)


        return diff_tokens


    def tokenize(self, script_diff):
        return self.extract_diff_tokens(script_diff)
