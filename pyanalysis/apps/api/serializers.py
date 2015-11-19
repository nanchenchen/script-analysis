from rest_framework import serializers, pagination
from pyanalysis.apps.corpus import models as corpus_models
from pyanalysis.apps.enhance import models as enhance_models


class DatasetSerializer(serializers.ModelSerializer):

    class Meta:
        model = corpus_models.Dataset
        fields = ('id', 'name', 'description', 'count',  )
        read_only_fields = ('id', 'name', 'description', 'count', )


class ScriptSerializer(serializers.ModelSerializer):

    call_counts = serializers.ListField(child=serializers.DictField())
    class Meta:
        model = corpus_models.Script
        fields = ('id', 'name', 'call_counts', )
        read_only_fields = ('id', 'name', 'call_counts', )

class ScriptContentSerializer(serializers.ModelSerializer):

    contents = serializers.CharField(required=True)

    class Meta:
        model = corpus_models.Script
        fields = ('id', 'name', 'contents', )
        read_only_fields = ('id', 'name', 'contents', )


class SimilaritySerializer(serializers.Serializer):
    source = serializers.IntegerField()
    target = serializers.IntegerField()
    similarity = serializers.FloatField()


class SimilarityGraphSerializer(serializers.Serializer):
    dataset = serializers.IntegerField(required=True)
    nodes = ScriptSerializer(many=True)
    links = SimilaritySerializer(many=True)


