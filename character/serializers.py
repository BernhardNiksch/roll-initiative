from rest_framework import serializers

from .models import CharacterClass, CharacterRace, Character
from equipment.serializers import (
    ArmorNameSerializer,
    CharacterAdventuringGearSerializer,
    CharacterArmorSerializer,
    CharacterToolSerializer,
    CharacterWeaponSerializer,
    ToolNameSerializer,
    WeaponNameSerializer,
)
from features.serializers import ClassFeatureNameSerializer


class CharacterClassListEntrySerializer(serializers.ModelSerializer):
    """
    Class to serialize entries in the character class list.
    """

    # primary_abilities = serializers.SerializerMethodField()
    # saving_throw_proficiencies = serializers.SerializerMethodField()

    class Meta:
        model = CharacterClass
        fields = [
            'id',
            'name',
            'description',
            'hit_die',
            "primary_abilities",
            "saving_throw_proficiencies",
        ]

    # @staticmethod
    # def get_primary_abilities(obj):
    #     return obj.get_primary_abilities_display()
    #
    # @staticmethod
    # def get_saving_throw_proficiencies(obj):
    #     return obj.get_saving_throw_proficiencies_display()


class CharacterClassSerializer(CharacterClassListEntrySerializer):
    """
    Class to serialize character class details.
    """

    armor_proficiencies = ArmorNameSerializer(many=True, required=False)
    weapon_proficiencies = WeaponNameSerializer(many=True, required=False)
    tool_proficiencies = ToolNameSerializer(many=True, required=False)
    features = ClassFeatureNameSerializer(
        source="characterclassfeature_set", many=True, required=False
    )

    class Meta:
        model = CharacterClass
        fields = [
            'id',
            'name',
            'description',
            'hit_die',
            "primary_abilities",
            "saving_throw_proficiencies",
            "armor_proficiencies",
            "tool_proficiencies",
            "weapon_proficiencies",
            "features",
        ]


class CharacterClassNameSerializer(serializers.ModelSerializer):
    """
    Serialize character class id and name.
    """

    class Meta:
        model = CharacterClass
        fields = ['id', 'name']


class CharacterRaceSerializer(serializers.ModelSerializer):
    """
    Serialize character race details for detail and list views.
    """

    class Meta:
        model = CharacterRace
        fields = "__all__"


class CharacterRaceNameSerializer(serializers.ModelSerializer):
    """
    Serialize character race id and name.
    """

    class Meta:
        model = CharacterRace
        fields = ['id', 'name']


class CharacterListEntrySerializer(serializers.ModelSerializer):
    """
    Class to serialize entries in the characters list.
    """

    race = CharacterRaceNameSerializer()
    character_class = CharacterClassNameSerializer()

    class Meta:
        model = Character
        fields = (
            "id", "title", "first_name", "last_name", "age", "level", "race", "character_class",
        )


class CharacterAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Character
        exclude = ["adventuring_gear", "armor", "tools", "weapons", "feats"]


class CharacterSerializer(serializers.ModelSerializer):
    """
    Serialize character details.
    """

    character_class = CharacterClassNameSerializer()
    race = CharacterRaceNameSerializer()

    class Meta:
        model = Character
        exclude = ["adventuring_gear", "armor", "tools", "weapons"]


class CharacterEquipmentSerializer(serializers.ModelSerializer):
    """
    Serialize character equipment details.
    """
    adventuring_gear = CharacterAdventuringGearSerializer(
        many=True, source="characteradventuringgear_set"
    )
    armor = CharacterArmorSerializer(many=True, source="characterarmor_set")
    tools = CharacterToolSerializer(many=True)
    weapons = CharacterWeaponSerializer(many=True, source="characterweapon_set")

    class Meta:
        model = Character
        fields = ["adventuring_gear", "armor", "tools", "weapons"]
