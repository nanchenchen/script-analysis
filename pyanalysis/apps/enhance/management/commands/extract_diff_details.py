import numpy as np
import path
from StringIO import StringIO
from time import time
import tokenize

from django.core.management.base import BaseCommand, make_option, CommandError
from django.db import transaction

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def tokenize_line(line):

    tokens = tokenize.generate_tokens(StringIO(line).readline)
    tokens_list = []
    for token in tokens:
        type = tokenize.tok_name[token[0]]
        text = token[1]
        tokens_list.append((type, text))
    return tokens_list


def LCS(seq1, seq2):
    len1 = len(seq1)
    len2 = len(seq2)
    dp = np.zeros((len1 + 1, len2 + 1))

    for idx1, seq1_ele in enumerate(seq1):
        for idx2, seq2_ele in enumerate(seq2):
            if seq1_ele == seq2_ele:
                dp[idx1 + 1][idx2 + 1] = dp[idx1][idx2] + 1
            else:
                dp[idx1 + 1][idx2 + 1] = max(dp[idx1 + 1][idx2], dp[idx1][idx2 + 1])

    return dp[len1][len2]


def editing_dist(seq1, seq2):
    len1 = len(seq1)
    len2 = len(seq2)
    dp = np.zeros((len1 + 1, len2 + 1))

    for idx1, seq1_ele in enumerate(seq1):
        for idx2, seq2_ele in enumerate(seq2):
            if seq1_ele == seq2_ele:
                dp[idx1 + 1][idx2 + 1] = dp[idx1][idx2]
            else:
                dp[idx1 + 1][idx2 + 1] = min(dp[idx1 + 1][idx2], dp[idx1][idx2 + 1]) + 1

    return dp[len1][len2] / max(len1, len2)


def matching(list1, list2):
    pass


# graph should be an adjacency matrix
def dijkstra(graph, src, tar):
    num_nodes = graph.shape[0] # get number of nodes from graph
    dist = np.zeros(num_nodes) + float('inf')
    prev_node = [None] * num_nodes
    visited = [False] * num_nodes

    # initialization with dist from src
    for idx, d in enumerate(graph[src]):
        if d != float('inf'):
            dist[idx] = d
            prev_node[idx] = src
    visited[src] = True

    num_visited = 1

    while num_visited < num_nodes:
        # find minimum dist
        min = float('inf')
        min_node = None
        for idx, d in enumerate(dist):
            if not visited[idx] and d < min:
                min = d
                min_node = idx

        visited[min_node] = True
        num_visited += 1

        # stop if find target
        if min_node == tar:
            break

        # update dist
        for idx, d in enumerate(graph[min_node]):
            if (dist[min_node] + d) < dist[idx]:
                dist[idx] = dist[min_node] + d
                prev_node[idx] = min_node

    path = [tar]
    current_node = tar    
    while prev_node[current_node] is not None:
        path = [prev_node[current_node]] + path
        current_node = prev_node[current_node]
        
    return path


# both graphs should be an adjacency matrix
def bipartite_matching(capacity_graph, cost_graph):
    pass

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
        diffs = ScriptDiff.objects.all()[1]

        # Step 1: Extract + and - lines
        diff_text = diffs.text
        diff_lines = diff_text.split('\n')[3:] # skip first few lines
        diff_lines_plus = filter(lambda x: x.startswith('+'), diff_lines)
        diff_lines_minus = filter(lambda x: x.startswith('-'), diff_lines)
        diff_lines_plus = [x[1:] for x in diff_lines_plus]   # remove + sign
        diff_lines_minus = [x[1:] for x in diff_lines_minus] # remove - sign

        # Step 1.5: Tokenize
        diff_lines_plus_t = [tokenize_line(line) for line in diff_lines_plus]   # tokenize
        diff_lines_minus_t = [tokenize_line(line) for line in diff_lines_minus]   # tokenize
        print diff_lines_plus_t
        print diff_lines_minus_t


        import pdb
        pdb.set_trace()
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