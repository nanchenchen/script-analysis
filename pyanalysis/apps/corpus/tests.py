from datetime import datetime

from unittest import skip
from django.test import TestCase

from pyanalysis.apps.corpus import models as corpus_models
from pyanalysis.apps.dimensions import registry

class DatasetModelTest(TestCase):
    def test_created_at_set(self):
        """Dataset.created_at should get set automatically."""
        dset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")
        self.assertIsInstance(dset.created_at, datetime)


class MessageModelTest(TestCase):
    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")

    def test_can_get_message(self):
        """Should be able to get messages from a dataset."""

        corpus_models.Message.objects.create(dataset=self.dataset, text="Some text")
        msgs = self.dataset.message_set.all()

        self.assertEquals(msgs.count(), 1)
        self.assertEquals(msgs.first().text, "Some text")


class GetExampleMessageTest(TestCase):
    def generate_some_messages(self, dataset):
        corpus_models.Message.objects.create(
            dataset=dataset,
            text="blah blah blah",
            time="2015-02-02T01:19:02Z",
            shared_count=0,
        )

        hashtag = corpus_models.Hashtag.objects.create(text="OurPriorities")
        msg = corpus_models.Message.objects.create(
            dataset=dataset,
            text="blah blah blah #%s" % hashtag.text,
            time="2015-02-02T01:19:02Z",
            shared_count=10,
        )
        msg.hashtags.add(hashtag)

        self.dimension_time = registry.get_dimension('time')
        self.dimension_hashtags = registry.get_dimension('hashtags')
        self.dimension_shared = registry.get_dimension('shares')

    def setUp(self):
        self.dataset = corpus_models.Dataset.objects.create(name="Test Corpus", description="My Dataset")
        self.generate_some_messages(self.dataset)


    def test_with_no_filters(self):
        """Empty filter settings should return all messages"""
        filters = {}
        msgs = self.dataset.get_example_messages(filters)
        self.assertEquals(msgs.count(), 2)

    def test_with_inclusive_filters(self):
        """Filters that include all the messages."""
        filters = [
            {
                "dimension": self.dimension_time,
                "min_time": "2015-02-02T01:19:02Z",
                "max_time": "2015-02-02T01:19:03Z"
            },
            {
                "dimension": self.dimension_time,
                "value": "2015-02-02T01:19:02Z",
            }
        ]

        msgs = self.dataset.get_example_messages(filters)
        self.assertEquals(msgs.count(), 2)

    def test_with_exclusive_filters(self):
        """Filters that exclude all the messages"""
        filters = [
            {
                "dimension": self.dimension_time,
                "min_time": "2015-02-02T01:19:03Z",
                "max_time": "2015-02-02T01:19:03Z"
            },
            {
                "dimension": self.dimension_time,
                "value": "2015-02-02T01:19:03Z",
            }
        ]
        msgs = self.dataset.get_example_messages(filters)
        self.assertEquals(msgs.count(), 0)

    def test_quantitative_filter(self):
        """Filter on a numeric field"""
        filters = [
            {
                "dimension": self.dimension_shared,
                "min": 5,
                "max": 15,
            },
        ]
        msgs = self.dataset.get_example_messages(filters)
        self.assertEquals(msgs.count(), 1)

    def test_value_match(self):
        """Filters that match just one message"""

        filters = [
            {
                "dimension": self.dimension_hashtags,
                "value": "OurPriorities",
            }
        ]
        msgs = self.dataset.get_example_messages(filters)
        self.assertEquals(msgs.count(), 1)

    def test_dataset_specific_examples(self):
        """Does not mix messages across datasets."""

        other_dataset = corpus_models.Dataset.objects.create(name="second test corpus", description="blah")
        self.generate_some_messages(other_dataset)

        filters = {}
        msgs = self.dataset.get_example_messages(filters)
        self.assertEquals(msgs.count(), 2)
