from django.db import models
from django.utils import timezone


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


class Script(models.Model):
    """
    A script is a file
    """

    dataset = models.ForeignKey(Dataset, related_name="scripts")
    """Which :class:`Dataset` the script belongs to"""

    name = models.CharField(max_length=256)

    last_modified = models.DateTimeField(default=timezone.now)

    @property
    def contents(self):
        return "".join(map(lambda x: x.text, self.lines.all()))

    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.__repr__()


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

