from django.db import models
from django.utils import timezone
from django.db.models import Count
from operator import itemgetter

class Dataset(models.Model):
    """A top-level dataset object containing scripts."""

    name = models.CharField(max_length=150)
    """The name of the dataset"""

    description = models.TextField()
    """A description of the dataset."""

    created_at = models.DateTimeField(auto_now_add=True)
    """The :py:class:`datetime.datetime` when the dataset was created."""

    def __unicode__(self):
        return self.name

    @property
    def count(self):
        return self.scripts.count()

    @property
    def script_list(self):
        return [{"id": x.id, "name": x.name} for x in self.scripts.all()]


class Script(models.Model):
    """
    A script is a file
    """

    dataset = models.ForeignKey(Dataset, related_name="scripts")
    """Which :class:`Dataset` the script belongs to"""

    name = models.CharField(max_length=256)

    last_modified = models.DateTimeField(default=timezone.now)

    @property
    def text(self):
        return "".join(map(lambda x: x.text, self.lines.all()))

    @property
    def call_counts(self):
        return self.calls.exclude(name__isnull=True).values('name').annotate(count=Count('name')).order_by('-count')

    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.__repr__()

    def extract_common_calls(self, another_script):

        own_call_set = set(map(lambda x: x.name, self.calls.all()))
        another_call_set = set(map(lambda x: x.name, another_script.calls.all()))

        common_set = own_call_set.intersection(another_call_set)

        return list(common_set)

    def get_lines_with_topics(self, model_id):
        lines_with_topics = []
        for line in self.lines.all():
            tokens = line.token_vector_elements.all()
            topics = []
            for token in tokens:
                token_topics = token.dic_token.topics.filter(model_id=model_id, scripts=self).all()

                topics.extend(map(lambda x: {'index': x.index, 'probability': x.token_scores.filter(token=token.dic_token)[0].probability}, token_topics))
            topics = sorted(topics, key=itemgetter('probability'), reverse=True)
            lines_with_topics.append({'text': line.text, 'topics': topics})

        return lines_with_topics


class Line(models.Model):
    """
    A model for each line of a script
    """

    class Meta:
        index_together = (
            ('script', 'number'),
        )

    script = models.ForeignKey(Script, related_name="lines")
    """Which :class:`Script` the line belongs to"""

    number = models.IntegerField(default=0)
    """Line number"""

    text = models.TextField(default="", blank=True, null=True)

    def __repr__(self):
        return str(self.number) + ": " + self.text

    def __unicode__(self):
        return self.__repr__()

class FunctionCall(models.Model):
    """
    A model for each function call in a script
    """

    script = models.ForeignKey(Script, related_name="calls")
    """Which :class:`Script` the token belongs to"""

    name = models.CharField(max_length=255, default="", blank=True, null=True, db_index=True)

    def __repr__(self):
        return str(self.script.name) + ": " + self.name

    def __unicode__(self):
        return self.__repr__()


class Token(models.Model):
    """
    A model for each token of a script
    """
    class Meta:
        index_together = (
            ('script', 'type'),
        )

    script = models.ForeignKey(Script, related_name="tokens")
    """Which :class:`Script` the token belongs to"""

    line = models.ForeignKey(Line, related_name="tokens")
    """Which :class:`Line` the token belongs to"""

    st_col = models.IntegerField(default=0)
    """starting position in a line"""

    ed_col = models.IntegerField(default=0)
    """ending position in a line"""

    type = models.CharField(max_length=32, default="", blank=True, null=True)

    text = models.TextField(default="", blank=True, null=True)

    def __repr__(self):
        return str(self.type) + ": " + self.text

    def __unicode__(self):
        return self.__repr__()

