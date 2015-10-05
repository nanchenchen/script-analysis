from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from pyanalysis.apps.corpus.models import Dataset, Script, Line
from django.db import transaction
import traceback
import sys
import path
from time import time, localtime
from django.conf import settings

import os
from stat import *
import datetime

class Command(BaseCommand):
    """
    Import a corpus of message data into the database.

    .. code-block :: bash

        $ python manage.py import_corpus <file_path>

    """
    args = '<script_filename> [...]'
    help = "Import a corpus into the database."
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dataset',
                    action='store',
                    dest='dataset',
                    help='Set a target dataset to add to'
        ),
    )

    def handle(self, *filenames, **options):

        if len(filenames) == 0:
            raise CommandError('At least one filename must be provided.')

        dataset = options.get('dataset', None)
        if not dataset:
            dataset = filenames[0]

        for f in filenames:
            if not path.path(f).exists():
                raise CommandError("Filename %s does not exist" % f)

        start = time()
        dataset_obj, created = Dataset.objects.get_or_create(name=dataset, description=dataset)
        if created:
            print "Created dataset '%s' (%d)" % (dataset_obj.name, dataset_obj.id)
        else:
            print "Adding to existing dataset '%s' (%d)" % (dataset_obj.name, dataset_obj.id)


        for i, script_filename in enumerate(filenames):
            with open(script_filename, 'rb') as fp:
                if len(filenames) > 1:
                    print "Reading file %d of %d %s" % (i + 1, len(filenames), script_filename)
                else:
                    print "Reading file %s" % script_filename

                st = os.stat(script_filename)
                last_modified = datetime.datetime(*localtime(st[ST_MTIME])[:6]).strftime('%Y-%m-%d %H:%M:%S')
                script = Script(dataset=dataset_obj, name=script_filename, last_modified=last_modified)
                script.save()

                importer = Importer(fp, script)
                importer.run()

        dataset_obj.save()

        
        print "Time: %.2fs" % (time() - start)


class Importer(object):


    def __init__(self, fp, script):
        self.fp = fp
        self.script = script
        self.number = 0


    def run(self):
        start = time()

        with transaction.atomic(savepoint=False):
            for line in self.fp:
                self.number += 1
                line_obj = Line(script=self.script, number=self.number, text=line)
                line_obj.save()

            print "%6.2fs | Finished %d lines." % (
            time() - start, self.number)

