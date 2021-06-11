from rest_framework import serializers

from .models import CharacterClassFeature


class ClassFeatureNameSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source="feat.id")
    name = serializers.ReadOnlyField(source="feat.name")

    class Meta:
        model = CharacterClassFeature
        fields = ["id", "name", "level"]
