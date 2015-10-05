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


class Script(models.Model):
    """
    A script is a file
    """
    class Meta:
        index_together = (
            ('dataset', 'name'),
            ('dataset', 'last_modified'),
        )

    dataset = models.ForeignKey(Dataset, related_name="scripts")
    """Which :class:`Dataset` the script belongs to"""

    name = models.CharField(max_length=256)

    last_modified = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return self.name

    def __unicode__(self):
        return self.__repr__()


class Line(models.Model):
    """
    A model for each line of a script
    """

    script = models.ForeignKey(Script, related_name="lines")
    """Which :class:`Script` the line belongs to"""

    number = models.IntegerField(default=1)
    """Line number"""

    text = models.TextField(default="", blank=True, null=True)

    def __repr__(self):
        return str(self.number) + ": " + self.text

    def __unicode__(self):
        return self.__repr__()

