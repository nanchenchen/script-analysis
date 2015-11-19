from django.db import models, transaction
from django.conf import settings

from fields import PositiveBigIntegerField
from pyanalysis.apps.corpus.models import Dataset, Script
from gensim.corpora import Dictionary as GensimDictionary
import gensim.similarities

# Create your models here.

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
            yield self.tokenize(script)

    def tokenize(self, script):
        return map(lambda x: x.text, script.tokens.all())

class Dictionary(models.Model):
    dataset = models.ForeignKey(Dataset, related_name="dictionary", null=True, blank=True, default=None)

    time = models.DateTimeField(auto_now_add=True)

    num_docs = PositiveBigIntegerField(default=0)
    num_pos = PositiveBigIntegerField(default=0)
    num_nnz = PositiveBigIntegerField(default=0)

    @property
    def gensim_dictionary(self):
        if not hasattr(self, '_gensim_dict'):
            setattr(self, '_gensim_dict', self._load_gensim_dictionary())
        return getattr(self, '_gensim_dict')

    def get_token_id(self, bow_index):
        if not hasattr(self, '_index2id'):
            g = self.gensim_dictionary
        try:
            return self._index2id[bow_index]
        except KeyError:
            return None

    def _load_gensim_dictionary(self):

        setattr(self, '_index2id', {})

        gensim_dict = GensimDictionary()
        gensim_dict.num_docs = self.num_docs
        gensim_dict.num_pos = self.num_pos
        gensim_dict.num_nnz = self.num_nnz

        for dic_token in self.dic_tokens.all():
            self._index2id[dic_token.index] = dic_token.id
            gensim_dict.token2id[dic_token.text] = dic_token.index
            gensim_dict.dfs[dic_token.index] = dic_token.document_frequency

        logger.info("Dictionary contains %d words" % len(gensim_dict.token2id))

        return gensim_dict

    def _populate_from_gensim_dictionary(self, gensim_dict):

        self.num_docs = gensim_dict.num_docs
        self.num_pos = gensim_dict.num_pos
        self.num_nnz = gensim_dict.num_nnz
        self.save()

        logger.info("Saving gensim dictionary of dataset '%d' in the database" % self.dataset.id)

        batch = []
        count = 0
        print_freq = 10000
        batch_size = 1000
        total_words = len(gensim_dict.token2id)

        for token, id in gensim_dict.token2id.iteritems():
            dict_token = DictToken(dictionary=self,
                        text=token,
                        index=id,
                        document_frequency=gensim_dict.dfs[id])
            batch.append(dict_token)
            count += 1

            if len(batch) > batch_size:
                DictToken.objects.bulk_create(batch)
                batch = []

                if settings.DEBUG:
                    # prevent memory leaks
                    from django.db import connection

                    connection.queries = []

            if count % print_freq == 0:
                logger.info("Saved %d / %d words in the database dictionary" % (count, total_words))

        if len(batch):
            DictToken.objects.bulk_create(batch)
            count += len(batch)

            logger.info("Saved %d / %d words in the database dictionary" % (count, total_words))

        return self

    @classmethod
    def _build_gensim_dictionary(cls, dataset, scripts):
        # build a dictionary
        logger.info("Building a dictionary from texts")
        tokenized_scripts = TokenLoader(dataset.scripts.all())
        gensim_dict = GensimDictionary(tokenized_scripts)

        dict_obj, created = cls.objects.get_or_create(dataset=dataset)

        dict_obj._populate_from_gensim_dictionary(gensim_dict)

        return dict_obj

    def _vectorize_corpus(self):

        import math

        logger.info("Saving document word vectors in corpus.")

        scripts = self.dataset.scripts.all()

        total_documents = self.num_docs
        gdict = self.gensim_dictionary
        count = 0
        total_count = scripts.count()
        batch = []
        batch_size = 1000
        print_freq = 10000

        tokenized_scripts = TokenLoader(scripts)

        for script in scripts:

            tokens = tokenized_scripts.tokenize(script)
            bow = gdict.doc2bow(tokens)
            num_tokens = len(tokens)

            for dic_token_index, dic_token_freq in bow:
                dic_token_id = self.get_token_id(dic_token_index)
                document_freq = gdict.dfs[dic_token_index]

                try:
                    tf = float(dic_token_freq) / float(num_tokens)
                    idf = math.log(total_documents / document_freq)
                    tfidf = tf * idf

                except:
                    import pdb
                    pdb.set_trace()

                batch.append(TokenVectorElement(
                                         dic_token_id=dic_token_id,
                                         dic_token_index=dic_token_index,
                                         frequency=dic_token_freq,
                                         tfidf=tfidf,
                                         script=script))
            count += 1

            if len(batch) > batch_size:
                TokenVectorElement.objects.bulk_create(batch)
                batch = []

                if settings.DEBUG:
                    # prevent memory leaks
                    from django.db import connection

                    connection.queries = []

            if count % print_freq == 0:
                logger.info("Saved word-vectors for %d / %d documents" % (count, total_count))

        if len(batch):
            TokenVectorElement.objects.bulk_create(batch)
            logger.info("Saved word-vectors for %d / %d documents" % (count, total_count))

        logger.info("Created %d word vector entries" % count)

    def load_sparse_matrix(self, use_tfidf=True):

        script_id_list = []
        results = []

        scripts = self.dataset.scripts.all()

        for script in scripts:
            script_id_list.append(script.id)
            results.append(map(lambda x: x.to_tuple(use_tfidf), script.token_vector_elements.all()))

        return script_id_list, results

    def calc_script_similarity_matrix(self):
        script_id_list, matrix = self.load_sparse_matrix()
        index = gensim.similarities.SparseMatrixSimilarity(matrix, num_features=self.dic_tokens.count())
        for r_idx, row in enumerate(matrix):
            sim_row = index[row]
            for c_idx, sim in enumerate(sim_row):
                sim_pair = SimilarityPair(src_script_id=script_id_list[r_idx],
                                          tar_script_id=script_id_list[c_idx],
                                          similarity=sim)
                sim_pair.save()

    def calc_script_common_call_num(self):
        scripts = self.dataset.scripts.all()
        sim_pair_list = []
        with transaction.atomic(savepoint=False):
            for i in range(len(scripts)):
                for j in range(i + 1, len(scripts)):
                    common_call_num = len(scripts[i].extract_common_calls(scripts[j]))
                    sim_pair_list.append(
                        SimilarityPair(type='common_calls',
                                       src_script_id=scripts[i].id,
                                       tar_script_id=scripts[j].id,
                                       similarity=common_call_num))

                SimilarityPair.objects.bulk_create(sim_pair_list)
                sim_pair_list = []


class DictToken(models.Model):
    dictionary = models.ForeignKey(Dictionary, related_name='dic_tokens')
    index = models.IntegerField()
    text = models.TextField(default="", blank=True, null=True)
    document_frequency = models.IntegerField()

    scripts = models.ManyToManyField(Script, through='TokenVectorElement', related_name='dic_tokens')

    def __repr__(self):
        return self.text

    def __unicode__(self):
        return self.__repr__()

class TokenVectorElement(models.Model):
    script = models.ForeignKey(Script, related_name="token_vector_elements")
    dic_token = models.ForeignKey(DictToken, related_name="token_vector_elements")

    frequency = models.IntegerField(default=0)
    dic_token_index = models.IntegerField(default=0)
    tfidf = models.FloatField(default=0.0)

    def to_tuple(self, use_tfidf=True):
        return (self.dic_token_index, self.tfidf) if use_tfidf else (self.dic_token_index, self.frequency)

class SimilarityPair(models.Model):
    type = models.CharField(max_length=32, default="cosine", null=False, blank=False, db_index=True)
    src_script = models.ForeignKey(Script, related_name="similarity_pairs", db_index=True)
    tar_script = models.ForeignKey(Script, db_index=True)
    similarity = models.FloatField(default=0.0)