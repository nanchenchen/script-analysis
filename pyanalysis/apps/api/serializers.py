from rest_framework import serializers, pagination
from pyanalysis.apps.corpus import models as corpus_models
from pyanalysis.apps.enhance import models as enhance_models


class DatasetSerializer(serializers.ModelSerializer):
    script_list = serializers.ListField(child=serializers.DictField())

    class Meta:
        model = corpus_models.Dataset
        fields = ('id', 'name', 'description', 'count', 'script_list', )
        read_only_fields = ('id', 'name', 'description', 'count', 'script_list', )


class ScriptSerializer(serializers.ModelSerializer):

    call_counts = serializers.ListField(child=serializers.DictField())
    class Meta:
        model = corpus_models.Script
        fields = ('id', 'name', 'call_counts', )
        read_only_fields = ('id', 'name', 'call_counts', )

class ScriptContentSerializer(serializers.ModelSerializer):

    text = serializers.CharField(required=True)

    class Meta:
        model = corpus_models.Script
        fields = ('id', 'name', 'text', )
        read_only_fields = ('id', 'name', 'text', )


class SimilaritySerializer(serializers.Serializer):
    source = serializers.IntegerField()
    target = serializers.IntegerField()
    similarity = serializers.FloatField()


class SimilarityGraphSerializer(serializers.Serializer):
    dataset = serializers.IntegerField(required=True)
    nodes = ScriptSerializer(many=True)
    links = SimilaritySerializer(many=True)

class ScriptComparatorSerializer(serializers.Serializer):
    source = ScriptContentSerializer()
    target = ScriptContentSerializer()
    diff = serializers.CharField()
    relative_relation = serializers.CharField(required=False)
    note = serializers.CharField(required=False)

class DifferenceNoteSerializer(serializers.ModelSerializer):

    relative_relation = serializers.CharField(required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = enhance_models.DifferenceNote
        fields = ('src_script', 'tar_script', 'relative_relation', 'note', )