import types
from django.db import transaction

from rest_framework import status
from rest_framework.views import APIView, Response
from django.db.models import F
from django.core.urlresolvers import NoReverseMatch
from rest_framework.reverse import reverse
from rest_framework.compat import get_resolver_match, OrderedDict
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.contrib.auth.models import User

from pyanalysis.apps.corpus import models as corpus_models
from pyanalysis.apps.enhance import models as enhance_models
from pyanalysis.apps.api import serializers

import json
import logging
class SimilarityGraphView(APIView):
    """
    Get similarity pairs

    **Request:** ``GET /api/similarity/id=1``
    """


    def get(self, request, format=None):
        if request.query_params.get('id'):
            dataset_id = int(request.query_params.get('id'))
            metric = request.query_params.get('metric')
            threshold = {
                'cosine': 0.1,
                'common_calls': 5
            }

            if metric is None:
                metric = "cosine"

            try:

                dataset = corpus_models.Dataset.objects.get(id=dataset_id)
                scripts = dataset.scripts.all()

                id_map = {}
                for idx, script in enumerate(scripts):
                    id_map[script.id] = idx

                similarity_pairs = []

                for script in scripts:
                    links = script.similarity_pairs.filter(type=metric, tar_script_id__gt=F('src_script_id'), similarity__gt=threshold[metric]).all()
                    for l in links:
                        src_id = id_map[l.src_script_id]
                        tar_id = id_map[l.tar_script_id]
                        similarity_pairs.append({'source': src_id, 'target': tar_id, 'similarity': l.similarity})


                results = {
                    "dataset": dataset_id,
                    "nodes": scripts,
                    "links": similarity_pairs}


                output = serializers.SimilarityGraphSerializer(results)

                return Response(output.data, status=status.HTTP_200_OK)

            except:
                import traceback
                traceback.print_exc()
                return Response("Dataset not exist", status=status.HTTP_400_BAD_REQUEST)

        return Response("Please specify dataset id", status=status.HTTP_400_BAD_REQUEST)

class ScriptContentView(APIView):
    """
    Get similarity pairs

    **Request:** ``GET /api/script?id=1``
    """


    def get(self, request, format=None):
        if request.query_params.get('id'):
            script_id = int(request.query_params.get('id'))
            try:

                script = corpus_models.Script.objects.get(id=script_id)
                output = serializers.ScriptContentSerializer(script)

                return Response(output.data, status=status.HTTP_200_OK)

            except:
                import traceback
                traceback.print_exc()
                return Response("Script not exist", status=status.HTTP_400_BAD_REQUEST)

        return Response("Please specify script id", status=status.HTTP_400_BAD_REQUEST)


class DatasetView(APIView):
    """
    Get details of a dataset

    **Request:** ``GET /api/dataset/1``
    """


    def get(self, request, format=None):
        if request.query_params.get('id'):
            dataset_id = int(request.query_params.get('id'))
            try:
                dataset = corpus_models.Dataset.objects.get(id=dataset_id)
                output = serializers.DatasetSerializer(dataset)
                return Response(output.data, status=status.HTTP_200_OK)
            except:
                return Response("Dataset not exist", status=status.HTTP_400_BAD_REQUEST)

        return Response("Please specify dataset id", status=status.HTTP_400_BAD_REQUEST)


class APIRoot(APIView):
    """
    The Text Visualization DRG Root API View.
    """
    root_urls = {}

    def get(self, request, *args, **kwargs):
        ret = OrderedDict()
        namespace = get_resolver_match(request).namespace
        for key, urlconf in self.root_urls.iteritems():
            url_name = urlconf.name
            if namespace:
                url_name = namespace + ':' + url_name
            try:
                ret[key] = reverse(
                    url_name,
                    request=request,
                    format=kwargs.get('format', None)
                )
                print ret[key]
            except NoReverseMatch:
                # Don't bail out if eg. no list routes exist, only detail routes.
                continue

        return Response(ret)
