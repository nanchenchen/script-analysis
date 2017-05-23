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


def filter_out_token(seq):
    remove_types = ['OP', #'COMMENT',
                    'ENDMARKER', 'NL']
    return filter(lambda (token_type, token_text): token_type not in remove_types, seq)

def editing_dist(seq1, seq2, mode='dist'):
    seq1 = filter_out_token(seq1)
    seq2 = filter_out_token(seq2)

    len1 = len(seq1)
    len2 = len(seq2)
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

def line_matching_by_lcs(list1, list2, matching_threshold=0.5):

    len1 = len(list1)
    len2 = len(list2)
    dp = np.zeros((len1 + 1, len2 + 1))

    dist = np.zeros((len1, len2)) + float('inf')
    for i in range(len1):
        for j in range(len2):
            dist[i][j] = editing_dist(list1[i], list2[j])

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

def matching(list1, list2):
    len1 = len(list1)
    len2 = len(list2)
    num_nodes = len1 + len2 + 2  # num of nodes is len1 + len2 + src + tar

    capacity_graph = np.zeros((num_nodes, num_nodes))
    cost_graph = np.zeros((num_nodes, num_nodes)) + float('inf')

    # node id:  src is 0, 1~len1 are for list1, (len1 + 1) ~ (len1 + len2) are for list 2, tar is num_nodes - 1
    src = 0
    list1_nodes = range(1, len1 + 1)
    list2_nodes = range(len1 + 1, len1 + len2 + 1)
    tar = num_nodes - 1

    # initialize src to list1 nodes
    for i in list1_nodes:
        capacity_graph[src][i] = 1
        cost_graph[src][i] = 0

    # initialize list2 nodes to tar
    for i in list2_nodes:
        capacity_graph[i][tar] = 1
        cost_graph[src][i] = 0

    for i, list1_node in enumerate(list1_nodes):
        for j, list2_node in enumerate(list2_nodes):
            capacity_graph[list1_node][list2_node] = 1
            cost_graph[list1_node][list2_node] = editing_dist(list1[i], list2[j])

    # TODO: run shortest path algorithm and update residual network


# graph should be an adjacency matrix with non-negative dist
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

    path_nodes = [tar]
    current_node = tar    
    while prev_node[current_node] is not None:
        path_nodes = [prev_node[current_node]] + path_nodes
        current_node = prev_node[current_node]
        
    return path_nodes


def floyd_warshall(graph):
    num_nodes = graph.shape[0]

    # initialization
    dist = np.zeros((num_nodes, num_nodes)) + float('inf')
    last_node = [[None] * num_nodes for i in range(num_nodes)]

    for i in range(num_nodes):
        for j in range(num_nodes):
            if i == j:
                dist[i][j] = 0
            elif graph[i][j] != float('inf'):
                dist[i][j] = graph[i][j]
                last_node[i][j] = i

    for k in range(num_nodes):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if dist[i][j] > (dist[i][k] + dist[k][j]):
                    dist[i][j] = dist[i][k] + dist[k][j]
                    last_node[i][j] = k

    return dist, last_node


def extract_fw_path(last_node, src, tar):
    path_nodes = [tar]
    current_node = tar
    while last_node[src][current_node] is not None:
        path_nodes = [last_node[src][current_node]] + path_nodes
        current_node = last_node[src][current_node]

    return path_nodes


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
        # diffs = ScriptDiff.objects.all()[4]
        diffs = ScriptDiff.objects.get(id=8)

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
        #print diff_lines_plus_t
        #print diff_lines_minus_t

        try:
            matching_items = line_matching_by_lcs(diff_lines_plus_t, diff_lines_minus_t)
            for (i, j) in matching_items:
                if i is not None and j is not None:
                    print "(%2d, %2d): %s\t|\t%s" %(i, j, diff_lines_plus[i], diff_lines_minus[j])
                    #print editing_dist(diff_lines_plus_t[i], diff_lines_minus_t[j], mode='diff')
                elif i is None and j is not None:
                    print "(  , %2d): --------\t|\t%s" %(j,  diff_lines_minus[j])
                    #print filter_out_token(diff_lines_minus_t[j])
                elif i is not None and j is None:
                    print "(%2d,   ): %s\t|\t--------" %(i,  diff_lines_plus[i])
                    #print filter_out_token(diff_lines_plus_t[i])
        except:
            import traceback
            traceback.print_exc()


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