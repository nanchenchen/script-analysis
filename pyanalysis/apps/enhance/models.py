import ntpath
import difflib

from django.db import models, transaction
from django.conf import settings

from fields import PositiveBigIntegerField
from gensim.corpora import Dictionary as GensimDictionary
import gensim.similarities
import editdistance

from pyanalysis.apps.corpus.models import Dataset, Script, Line
from pyanalysis.apps.enhance.tokenizers import *

# Create your models here.

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Dictionary(models.Model):
    name = models.CharField(max_length=100, null=True, default="", blank=True)
    dataset = models.ForeignKey(Dataset, related_name="dictionary", null=True, blank=True, default=None)
    settings = models.TextField(default="", blank=True, null=True)


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

        logger.info("Dictionary contains %d tokens" % len(gensim_dict.token2id))

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
        total_tokens = len(gensim_dict.token2id)

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
                logger.info("Saved %d / %d tokens in the database dictionary" % (count, total_tokens))

        if len(batch):
            DictToken.objects.bulk_create(batch)
            count += len(batch)

            logger.info("Saved %d / %d tokens in the database dictionary" % (count, total_tokens))

        return self

    @classmethod
    def _build_gensim_dictionary(cls, dataset, scripts):
        # build a dictionary
        logger.info("Building a dictionary from texts")
        tokenized_scripts = CallTokenLoader(dataset.scripts.all())
        gensim_dict = GensimDictionary(tokenized_scripts)

        dict_obj, created = cls.objects.get_or_create(dataset=dataset)

        dict_obj._populate_from_gensim_dictionary(gensim_dict)

        return dict_obj


    @classmethod
    def _create_from_texts(cls, tokenized_texts, name, dataset, settings, minimum_frequency=2):
        from gensim.corpora import Dictionary as GensimDictionary

        # build a dictionary
        logger.info("Building a dictionary from texts")
        dictionary = GensimDictionary(tokenized_texts)

        # Remove extremely rare words
        logger.info("Dictionary contains %d words. Filtering..." % len(dictionary.token2id))
        dictionary.filter_extremes(no_below=minimum_frequency, no_above=1, keep_n=None)
        dictionary.compactify()
        logger.info("Dictionary contains %d words." % len(dictionary.token2id))

        dict_model = cls(name=name,
                         dataset=dataset,
                         settings=settings)
        dict_model.save()

        dict_model._populate_from_gensim_dictionary(dictionary)

        return dict_model


    def _vectorize_corpus(self, queryset, tokenizer):

        import math

        logger.info("Saving document token vectors in corpus.")

        total_documents = self.num_docs
        gdict = self.gensim_dictionary
        count = 0
        total_count = queryset.count()
        batch = []
        batch_size = 1000
        print_freq = 10000

#        tokenized_scripts = tokenizer(scripts)

        for script in queryset.iterator():
            for line in script.lines.all():
                tokens = tokenizer.tokenize(line)
                bow = gdict.doc2bow(tokens)
                num_tokens = len(tokens)

                for dic_token_index, dic_token_freq in bow:
                    dic_token_id = self.get_token_id(dic_token_index)
                    document_freq = gdict.dfs[dic_token_index]

                    try:
                        tf = float(dic_token_freq)
                        idf = math.log(total_documents / document_freq)
                        tfidf = tf * idf

                    except:
                        import pdb
                        pdb.set_trace()

                    batch.append(TokenVectorElement(
                                             dictionary=self,
                                             dic_token_id=dic_token_id,
                                             dic_token_index=dic_token_index,
                                             frequency=dic_token_freq,
                                             tfidf=tfidf,
                                             line=line,
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
                    logger.info("Saved token-vectors for %d / %d documents" % (count, total_count))

        if len(batch):
            TokenVectorElement.objects.bulk_create(batch)
            logger.info("Saved token-vectors for %d / %d documents" % (count, total_count))

        logger.info("Created %d token vector entries" % count)


    def _build_lda(self, name, corpus, num_topics=30, tokens_to_save=200, multicore=True):
        from gensim.models import LdaMulticore, LdaModel

        gdict = self.gensim_dictionary

        if multicore:
            lda = LdaMulticore(corpus=corpus,
                               num_topics=num_topics,
                               workers=3,
                               id2word=gdict)
        else:
            lda = LdaModel(corpus=corpus,
                               num_topics=num_topics,
                               id2word=gdict)

        model = TopicModel(name=name, dictionary=self)
        model.save()

        topics = []
        for i in range(num_topics):
            topic = lda.show_topic(i, topn=tokens_to_save)
            alpha = lda.alpha[i]

            topicm = Topic(model=model, name="?", alpha=alpha, index=i)
            topicm.save()
            topics.append(topicm)

            tokens = []
            for token_text, prob in topic:
                token_index = gdict.token2id[token_text]
                token_id = self.get_token_id(token_index)
                tw = TopicDictToken(topic=topicm,
                               token_id=token_id, token_index=token_index,
                               probability=prob)
                tokens.append(tw)
            TopicDictToken.objects.bulk_create(tokens)

            most_likely_token_scores = topicm.token_scores\
                .order_by('-probability')\
                .prefetch_related('token')

            topicm.name = ', '.join([score.token.text for score in most_likely_token_scores[:3]])
            topicm.save()

            if settings.DEBUG:
                # prevent memory leaks
                from django.db import connection

                connection.queries = []

        model.save_to_file(lda)

        return (model, lda)

    def _apply_lda(self, model, corpus, lda=None):

        if lda is None:
            # recover the lda
            lda = model.load_from_file()

        total_documents = len(corpus)
        count = 0
        batch = []
        batch_size = 1000
        print_freq = 10000

        topics = list(model.topics.order_by('index'))

        # Go through the bows and get their topic mixtures
        for bow in corpus:
            mixture = lda.get_document_topics(bow)
            script_id = corpus.current_script_id

            for topic_index, prob in mixture:
                topic = topics[topic_index]
                itemtopic = ScriptTopic(topic_model=model,
                                         topic=topic,
                                         script_id=script_id,
                                         probability=prob)
                batch.append(itemtopic)

            count += 1

            if len(batch) > batch_size:
                ScriptTopic.objects.bulk_create(batch)
                batch = []

                if settings.DEBUG:
                    # prevent memory leaks
                    from django.db import connection

                    connection.queries = []

            if count % print_freq == 0:
                logger.info("Saved topic-vectors for %d / %d documents" % (count, total_documents))

        if len(batch):
            ScriptTopic.objects.bulk_create(batch)
            logger.info("Saved topic-vectors for %d / %d documents" % (count, total_documents))

    def _evaluate_lda(self, model, corpus, lda=None):

        if lda is None:
            # recover the lda
            lda = model.load_from_file()

        logger.info("Calculating model perplexity on entire corpus...")
        model.perplexity = lda.log_perplexity(corpus)
        logger.info("Perplexity: %f" % model.perplexity)
        model.save()

    def load_sparse_matrix(self, use_tfidf=True):

        script_id_list = []
        results = []

        scripts = self.dataset.scripts.all()

        for script in scripts:
            script_id_list.append(script.id)
            tokens = map(lambda x: x.to_tuple(use_tfidf), script.token_vector_elements.all())
            results.append(filter(lambda x: x[1] > 0, tokens))

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
    def calc_script_name_similarity(self):
        scripts = self.dataset.scripts.all()
        sim_pair_list = []
        with transaction.atomic(savepoint=False):
            for i in range(len(scripts)):
                for j in range(i + 1, len(scripts)):
                    name_similarity = editdistance.eval(ntpath.basename(scripts[i].name),
                                                        ntpath.basename(scripts[j].name))
                    sim_pair_list.append(
                        SimilarityPair(type='name_similarity',
                                       src_script_id=scripts[i].id,
                                       tar_script_id=scripts[j].id,
                                       similarity=name_similarity))

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

class TopicModel(models.Model):
    dictionary = models.ForeignKey(Dictionary)

    name = models.TextField(default="", blank=True)
    description = models.CharField(max_length=200)

    time = models.DateTimeField(auto_now_add=True)
    perplexity = models.FloatField(default=0)

    def load_from_file(self):
        from gensim.models import LdaMulticore

        return LdaMulticore.load("lda_out_%d.model" % self.id)

    def save_to_file(self, gensim_lda):
        gensim_lda.save("lda_out_%d.model" % self.id)

    def get_probable_topic(self, script):
        """For this model, get the most likely topic for the script."""
        script_topics = script.topic_probabilities\
            .filter(topic_model=self)\
            .only('topic', 'probability')

        max_prob = -100000
        probable_topic = None
        for mt in script_topics:
            if mt.probability > max_prob:
                probable_topic = mt.topic
                max_prob = mt.probability

        return probable_topic


class Topic(models.Model):
    model = models.ForeignKey(TopicModel, related_name='topics')
    name = models.TextField(default="", blank=True)
    description = models.CharField(max_length=200)
    index = models.IntegerField()
    alpha = models.FloatField()

    scripts = models.ManyToManyField(Script, through='ScriptTopic', related_name='topics')
    tokens = models.ManyToManyField(DictToken, through='TopicDictToken', related_name='topics')


class TopicDictToken(models.Model):
    token = models.ForeignKey(DictToken, related_name='topic_scores')
    topic = models.ForeignKey(Topic, related_name='token_scores')

    token_index = models.IntegerField()
    probability = models.FloatField()

class ScriptTopic(models.Model):
    class Meta:
        index_together = (
            ('topic_model', 'script'),
            ('script', 'topic'),
        )

    topic_model = models.ForeignKey(TopicModel, db_index=False)

    topic = models.ForeignKey(Topic, related_name='script_probabilities')
    script = models.ForeignKey(Script, related_name="topic_probabilities", db_index=False)

    probability = models.FloatField()


    @classmethod
    def get_examples(cls, topic):
        examples = cls.objects.filter(topic=topic, probability__gte=0.5).distinct()
        return examples.order_by('-probability')


class TokenVectorElement(models.Model):
    dictionary = models.ForeignKey(Dictionary, db_index=False, default=None, null=True, blank=True)

    script = models.ForeignKey(Script, related_name="token_vector_elements")
    dic_token = models.ForeignKey(DictToken, related_name="token_vector_elements")
    line = models.ForeignKey(Line, related_name="token_vector_elements", default=None, null=True, blank=True)

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

    def get_diff(self):
        source = self.src_script
        target = self.tar_script

        diff = "\n".join(difflib.unified_diff(source.text.split('\n'), target.text.split('\n'), fromfile=source.name, tofile=target.name))

        return diff


class DifferenceNote(models.Model):
    src_script = models.ForeignKey(Script, related_name="difference_notes")
    tar_script = models.ForeignKey(Script)

    RELATION_CHOICES = (
        ('<', 'src is older'),
        ('=', 'may be the same'),
        ('>', 'tar is older'),
        ('?', 'tar is older'),
        ('U', 'Undefined'),
    )
    relative_relation = models.CharField(max_length=1, choices=RELATION_CHOICES, default='U')

    note = models.TextField(default="", blank=True)

    class Meta:
        index_together = (
            "src_script", "tar_script"
        )


class ScriptDiff(models.Model):
    """
    Script diff between two files
    """

    pair = models.ForeignKey(SimilarityPair, related_name="diff", unique=True)
    text = models.TextField(default="", blank=True, null=True)