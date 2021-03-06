

from models import Dictionary
from pyanalysis.apps.corpus.models import Dataset, Script
from pyanalysis.apps.enhance.models import Dictionary, TokenVectorElement, DiffTokenVectorElement
from pyanalysis.apps.enhance.tokenizers import *

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class DbTextIterator(object):
    def __init__(self, queryset):
        self.queryset = queryset
        self.current_position = 0
        self.current = None

    def __iter__(self):
        self.current_position = 0
        for script in self.queryset.iterator():
            self.current = script
            self.current_position += 1
            if self.current_position % 10000 == 0:
                logger.info("Iterating through database texts: item %d" % self.current_position)

            yield script


class DbWordVectorIterator(object):
    def __init__(self, dictionary, freq_field='tfidf'):
        self.dictionary = dictionary
        self.freq_field = freq_field
        self.current_script_id = None
        self.current_vector = None

    def __iter__(self):
        qset = TokenVectorElement.objects.filter(dictionary=self.dictionary).order_by('script')
        self.current_script_id = None
        self.current_vector = []
        current_position = 0
        for mw in qset.iterator():
            script_id = mw.script_id
            token_idx = mw.dic_token_index
            freq = getattr(mw, self.freq_field)

            if self.current_script_id is None:
                self.current_script_id = script_id
                self.current_vector = []

            if self.current_script_id != script_id:
                yield self.current_vector
                self.current_vector = []
                self.current_script_id = script_id
                current_position += 1

                if current_position % 10000 == 0:
                    logger.info("Iterating through database token-vectors: item %d" % current_position)

            self.current_vector.append((token_idx, freq))

        # one more extra one
        yield self.current_vector

    def __len__(self):
        from django.db.models import Count

        count = TokenVectorElement.objects \
            .filter(dictionary=self.dictionary) \
            .aggregate(Count('script', distinct=True))

        if count:
            return count['script__count']

class DbDiffTokenVectorIterator(object):
    def __init__(self, dictionary, freq_field='tfidf'):
        self.dictionary = dictionary
        self.freq_field = freq_field
        self.current_script_diff_id = None
        self.current_vector = None

    def __iter__(self):
        qset = DiffTokenVectorElement.objects.filter(dictionary=self.dictionary).order_by('script_diff')
        self.current_script_diff_id = None
        self.current_vector = []
        current_position = 0
        for mw in qset.iterator():
            script_diff_id = mw.script_diff_id
            token_idx = mw.dic_token_index
            freq = getattr(mw, self.freq_field)

            if self.current_script_diff_id is None:
                self.current_script_diff_id = script_diff_id
                self.current_vector = []

            if self.current_script_diff_id != script_diff_id:
                yield self.current_vector
                self.current_vector = []
                self.current_script_diff_id = script_diff_id
                current_position += 1

                if current_position % 10000 == 0:
                    logger.info("Iterating through database token-vectors: item %d" % current_position)

            self.current_vector.append((token_idx, freq))

        # one more extra one
        yield self.current_vector

    def __len__(self):
        from django.db.models import Count

        count = DiffTokenVectorElement.objects \
            .filter(dictionary=self.dictionary) \
            .aggregate(Count('script_diff', distinct=True))

        if count:
            return count['script_diff__count']



class TopicContext(object):
    def __init__(self, name, queryset, tokenizer, filters, minimum_frequency=4):
        self.name = name
        self.queryset = queryset
        self.tokenizer = tokenizer
        self.filters = filters
        self.minimum_frequency = minimum_frequency

    def queryset_str(self):
        return str(self.queryset.query)

    def get_dict_settings(self):
        settings = dict(
            name=self.name,
            tokenizer=self.tokenizer.__name__,
            dataset=self.queryset_str(),
            filters=repr(self.filters),
            minimum_frequency=self.minimum_frequency
        )

        import json

        return json.dumps(settings, sort_keys=True)


    def find_dictionary(self):
        results = Dictionary.objects.filter(settings=self.get_dict_settings())
        return results.last()


    def build_dictionary(self, dataset_id):
        texts = DbTextIterator(self.queryset)

        tokenized_texts = self.tokenizer(texts, *self.filters)
        dataset = Dataset.objects.get(pk=dataset_id)
        return Dictionary._create_from_texts(tokenized_texts=tokenized_texts,
                                             name=self.name,
                                             minimum_frequency=self.minimum_frequency,
                                             dataset=dataset,
                                             settings=self.get_dict_settings())

    def bows_exist(self, dictionary):
        return TokenVectorElement.objects.filter(dictionary=dictionary).exists()


    def build_bows(self, dictionary):
        texts = DbTextIterator(self.queryset)
        tokenized_texts = self.tokenizer(texts, *self.filters)

        dictionary._vectorize_corpus(queryset=self.queryset,
                                     tokenizer=tokenized_texts)

    def build_lda(self, dictionary, num_topics=30, **kwargs):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._build_lda(self.name, corpus, num_topics=num_topics, **kwargs)

    def apply_lda(self, dictionary, model, lda=None):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._apply_lda(model, corpus, lda=lda)

    def evaluate_lda(self, dictionary, model, lda=None):
        corpus = DbWordVectorIterator(dictionary)
        return dictionary._evaluate_lda(model, corpus, lda=lda)


class LambdaWordFilter(object):
    def __init__(self, fn):
        self.fn = fn

    def __contains__(self, item):
        return self.fn(item)


def standard_topic_pipeline(context, dataset_id, num_topics, **kwargs):
    dictionary = context.find_dictionary()
    if dictionary is None:
        logger.info("Dictionary does not exist. Creating...")
        dictionary = context.build_dictionary(dataset_id=dataset_id)

    if not context.bows_exist(dictionary):
        logger.info("Bag of words does not exist. Creating...")
        context.build_bows(dictionary)

    logger.info("Building LDA")
    model, lda = context.build_lda(dictionary, num_topics=num_topics, **kwargs)
    context.apply_lda(dictionary, model, lda)
    context.evaluate_lda(dictionary, model, lda)


def default_topic_context(name, dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)
    queryset = dataset.scripts.all()

    filters = [
        LambdaWordFilter(lambda word: word == 'len' or word == 'int'),
       # LambdaWordFilter(lambda word: word.startswith('http') and len(word) > 4)
    ]

    return TopicContext(name=name, queryset=queryset,
                        tokenizer=CallTokenLoader,
                        filters=filters,
                        minimum_frequency=2)




def build_script_dictionary(dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)

    dictionary = Dictionary._build_gensim_dictionary(dataset=dataset, scripts=dataset.scripts.all() )
    dictionary._vectorize_corpus()


class DiffTopicContext(TopicContext):
    def bows_exist(self, dictionary):
        return DiffTokenVectorElement.objects.filter(dictionary=dictionary).exists()

    def build_bows(self, dictionary):
        texts = DbTextIterator(self.queryset)
        tokenized_texts = self.tokenizer(texts, *self.filters)

        dictionary._vectorize_diff_corpus(queryset=self.queryset,
                                          tokenizer=tokenized_texts)

    def build_lda(self, dictionary, num_topics=30, **kwargs):
        corpus = DbDiffTokenVectorIterator(dictionary)
        return dictionary._build_lda(self.name, corpus, num_topics=num_topics, **kwargs)

    def apply_lda(self, dictionary, model, lda=None):
        corpus = DbDiffTokenVectorIterator(dictionary)
        return dictionary._apply_diff_lda(model, corpus, lda=lda)

    def evaluate_lda(self, dictionary, model, lda=None):
        corpus = DbDiffTokenVectorIterator(dictionary)
        return dictionary._evaluate_lda(model, corpus, lda=lda)

def diff_topic_context(name, dataset_id):
    from pyanalysis.apps.enhance.models import ScriptDiff
    diffs = ScriptDiff.objects.filter(pair__src_script__dataset_id=dataset_id)
    queryset = diffs.all()

    filters = [

    ]

    return DiffTopicContext(name=name, queryset=queryset,
                        tokenizer=DiffTokenLoader,
                        filters=filters,
                        minimum_frequency=1)