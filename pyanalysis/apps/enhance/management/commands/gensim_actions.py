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
        make_option('-a', '--action',
                    default='all',
                    dest='action',
                    help='Action to run [all|similarity]'
        ),

    )

    def handle(self, dataset_id, **options):

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        action = options.get('action')

        from pyanalysis.apps.enhance.models import Dictionary
        dictionary = Dictionary.objects.get(dataset_id=dataset_id)
        if action == 'all' or action == 'similarity':
            logger.info("Calculating consine similarity...")
            dictionary.calc_script_similarity_matrix()

        if action == 'all' or action == 'common_calls':
            logger.info("Calculating num of common calls...")
            dictionary.calc_script_common_call_num()


        if action == 'all' or action == 'lda':
            import gensim
            id2word=dictionary.gensim_dictionary
            script_ids, m = dictionary.load_sparse_matrix()
            lda = gensim.models.ldamodel.LdaModel(corpus=m, id2word=id2word, num_topics=10, iterations=500)
            lda.print_topics(10)


        if action == 'all' or action == 'kmean':
            import gensim
            script_ids, m = dictionary.load_sparse_matrix()
            mm = gensim.matutils.corpus2csc(m)

            from sklearn.cluster import KMeans
            num_clusters = 5
            km = KMeans(n_clusters=num_clusters)
            km.fit(mm)
            clusters = km.labels_.tolist()
            print clusters