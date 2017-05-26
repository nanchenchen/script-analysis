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
from pyanalysis.apps.enhance.analyses import get_script_var_graph, convert_format
from pyanalysis.apps.api import serializers

import json
import logging
class SimilarityGraphView(APIView):
    """
    Get similarity pairs

    **Request:** ``GET /api/similarity/?id=1``
    """


    def get(self, request, format=None):
        if request.query_params.get('id'):
            dataset_id = int(request.query_params.get('id'))
            metric = request.query_params.get('metric')
            threshold = {
                'cosine': 0.1,
                'common_calls': 5,
                'name_similarity': 0.75
            }

            if metric is None:
                metric = "cosine"

            if request.query_params.get('threshold'):
                threshold[metric] = float(request.query_params.get('threshold'))

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
                        if metric == "name_similarity":
                            similarity_pairs.append({'source': src_id, 'target': tar_id, 'similarity': 1 / (l.similarity + 1e-5)})

                        else:
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

class ScriptComparatorView(APIView):
    """
    Get similarity pairs

    **Request:** ``GET /api/comparator/?id=1&src_id=237&tar_id=241``
    """


    def get(self, request, format=None):
        if request.query_params.get('id') and request.query_params.get('src_id') and request.query_params.get('tar_id'):
            dataset_id = request.query_params.get('id')
            src_id = request.query_params.get('src_id')
            tar_id = request.query_params.get('tar_id')


            try:

                dataset = corpus_models.Dataset.objects.get(id=dataset_id)
                source = dataset.scripts.get(id=src_id)
                target = dataset.scripts.get(id=tar_id)

                import difflib
                diff = "\n".join(difflib.unified_diff(source.text.split('\n'), target.text.split('\n'), fromfile=source.name, tofile=target.name))

                note = ""
                relative_relation = "U"
                note_obj = enhance_models.DifferenceNote.objects.filter(src_script=source,
                                                                        tar_script=target).first()
                if note_obj:
                    note = note_obj.note
                    relative_relation = note_obj.relative_relation

                results = {
                    "source": source,
                    "target": target,
                    "diff": diff,
                    "relative_relation": relative_relation,
                    "note": note
                }

                output = serializers.ScriptComparatorSerializer(results)

                return Response(output.data, status=status.HTTP_200_OK)

            except:
                import traceback
                traceback.print_exc()
                return Response("Dataset not exist", status=status.HTTP_400_BAD_REQUEST)

        return Response("Please specify dataset id", status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, format=None):
        input = serializers.DifferenceNoteSerializer(data=request.data)
        if input.is_valid():
            data = input.validated_data

            source = data["src_script"]
            target = data["tar_script"]
            note_obj = enhance_models.DifferenceNote.objects.filter(src_script=source,
                                                                    tar_script=target).first()
            if note_obj is None:
                note_obj = enhance_models.DifferenceNote(src_script=source,
                                                         tar_script=target)

            note_obj.note = data["note"]
            note_obj.relative_relation = data["relative_relation"]
            note_obj.save()

            output = serializers.DifferenceNoteSerializer(note_obj)
            return Response(output.data, status=status.HTTP_200_OK)
        return Response(input.errors, status=status.HTTP_400_BAD_REQUEST)


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

class ScriptVariableGraphView(APIView):
    """
    Get similarity pairs

    **Request:** ``GET /api/vargraph?id=1``
    """


    def get(self, request, format=None):
        if request.query_params.get('id'):
            script_id = int(request.query_params.get('id'))
            try:

                script = corpus_models.Script.objects.get(id=script_id)
                variables = get_script_var_graph(script.text)
                output = convert_format(variables)
                output["name"] = script.name
                output["text"] = script.text

                return Response(output, status=status.HTTP_200_OK)

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

class DatasetRelationGraphView(APIView):
    """
    Get relations in a dataset

    **Request:** ``GET /api/relation/1``
    """


    def get(self, request, dataset_id, format=None):


        try:
            dataset = corpus_models.Dataset.objects.get(id=dataset_id)

            scripts = dataset.scripts.all()
            diff_notes = enhance_models.DifferenceNote.objects.filter(src_script__dataset_id=dataset_id).all()

            script_map = {}
            nodes = []
            node_map = {}
            node_idx = 0

            links = []

            for script in scripts:
                script_map[script.id] = script
                #node_map[script.id] = idx

            for diff in diff_notes:
                source = None
                target = None
                note = diff.note
                relation = None
                if diff.relative_relation != '>' and diff.relative_relation != '<':
                    continue
                if diff.src_script_id not in node_map:
                    node_map[diff.src_script_id] = node_idx
                    nodes.append({
                        "id": node_idx,
                        "original_id": diff.src_script_id,
                        "name": script_map[diff.src_script_id].name
                    })
                    node_idx += 1

                if diff.tar_script_id not in node_map:
                    node_map[diff.tar_script_id] = node_idx
                    nodes.append({
                        "id": node_idx,
                        "original_id": diff.tar_script_id,
                        "name": script_map[diff.tar_script_id].name
                    })
                    node_idx += 1

                if diff.relative_relation == '>':
                    source = node_map[diff.tar_script_id]
                    target = node_map[diff.src_script_id]
                    relation = 'D'

                else:
                    source = node_map[diff.src_script_id]
                    target = node_map[diff.tar_script_id]
                    if diff.relative_relation == '<':
                        relation = 'D'
                    elif diff.relative_relation == '=':
                        relation = 'E'
                    else:
                        relation = 'U'

                links.append({
                    "source": source,
                    "target": target,
                    "relation": relation,
                    "note": note

                })


            results = {
                "dataset": dataset_id,
                "nodes": nodes,
                "links": links
            }

            output = serializers.DatasetRelationGraphSerializer(results)
            return Response(output.data, status=status.HTTP_200_OK)
        except:
            import traceback
            traceback.print_exc()
            import pdb
            pdb.set_trace()
            return Response("Dataset not exist", status=status.HTTP_400_BAD_REQUEST)




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
