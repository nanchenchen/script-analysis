from django.contrib import admin

from pyanalysis.apps.corpus import models
admin.site.register(models.Dataset)
admin.site.register(models.Script)
admin.site.register(models.Line)

