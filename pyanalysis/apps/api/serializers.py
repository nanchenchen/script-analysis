from rest_framework import serializers, pagination
from pyanalysis.apps.corpus import models as corpus_models
from pyanalysis.apps.enhance import models as enhance_models


class ScriptSerializer(serializers.ModelSerializer):

    class Meta:
        model = corpus_models.Script
        fields = ('id', 'name', )
        read_only_fields = ('id', 'name', )


class SimilaritySerializer(serializers.Serializer):
    source = serializers.IntegerField()
    target = serializers.IntegerField()
    similarity = serializers.FloatField()


class SimilarityGraphSerializer(serializers.Serializer):
    dataset = serializers.IntegerField(required=True)
    nodes = ScriptSerializer(many=True)
    links = SimilaritySerializer(many=True)
