from models import Dictionary
from pyanalysis.apps.corpus.models import Dataset


# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def build_script_dictionary(dataset_id):
    dataset = Dataset.objects.get(pk=dataset_id)

    dictionary = Dictionary._build_gensim_dictionary(dataset=dataset, scripts=dataset.scripts.all() )
    dictionary._vectorize_corpus()

