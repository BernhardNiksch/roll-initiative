from rest_framework import serializers

from .models import Monster, MonsterType


class MonsterTypeNameSerializer(serializers.ModelSerializer):
    """
    Basic name serializer for nested MonsterType fields.
    """

    class Meta:
        model = MonsterType
        fields = ["id", "name"]


class MonsterTypeSerializer(serializers.ModelSerializer):
    """
    Serialize monster type object for list and detail view.
    """

    class Meta:
        model = MonsterType
        fields = "__all__"


class MonsterListEntrySerializer(serializers.ModelSerializer):
    """
    Serialize monster objects for list view.
    """

    monster_type = MonsterTypeNameSerializer()

    class Meta:
        model = Monster
        fields = ["id", "monster_type", "first_name", "last_name", "armor_class", "max_hp"]


class MonsterSerializer(MonsterListEntrySerializer):
    """
    Serialize Monster object for detail view
    """

    class Meta:
        model = Monster
        fields = "__all__"
