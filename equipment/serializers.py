from rest_framework import serializers

from equipment.models import (
    AdventuringGear,
    Armor,
    CharacterAdventuringGear,
    CharacterArmor,
    CharacterWeapon,
    EquipmentPack,
    EquipmentPackGear,
    Tool,
    Weapon,
)


class AdventuringGearSerializer(serializers.ModelSerializer):
    """
    Serialize AdventuringGear objects for detail and list views.
    """

    class Meta:
        model = AdventuringGear
        fields = "__all__"


class ArmorNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Armor
        fields = ["id", "name"]


class ArmorSerializer(serializers.ModelSerializer):
    """
    Serialize Armor objects for detail and list views.
    """

    armor_type = serializers.SerializerMethodField()

    class Meta:
        model = Armor
        fields = "__all__"

    @staticmethod
    def get_armor_type(obj):
        return obj.get_armor_type_display()


class CharacterAdventuringGearSerializer(serializers.ModelSerializer):
    """
    All you need to know about the gear assigned to your character.
    """

    id = serializers.CharField(source="adventuring_gear_id")
    name = serializers.CharField(source="adventuring_gear.name")
    weight = serializers.SerializerMethodField()

    class Meta:
        model = CharacterAdventuringGear
        fields = ["id", "name", "length", "quantity", "weight"]

    @staticmethod
    def get_weight(obj):
        return obj.weight()


class CharacterArmorSerializer(serializers.ModelSerializer):
    """
    Serialize details of the armor owned by the character and whether it is donned/equipped.
    """

    id = serializers.CharField(source="armor.id")
    name = serializers.CharField(source="armor.name")
    weight = serializers.CharField(source="armor.weight")
    armor_class = serializers.IntegerField(source="armor.armor_class")
    armor_class_increase = serializers.IntegerField(source="armor.armor_class_increase")
    armor_type = serializers.SerializerMethodField()

    class Meta:
        model = CharacterArmor
        fields = [
            "id", "name", "weight", "equipped", "armor_class", "armor_class_increase", "armor_type"
        ]

    @staticmethod
    def get_armor_type(obj):
        return obj.armor.get_armor_type_display()


class CharacterToolSerializer(serializers.ModelSerializer):
    """
    Serialize tools owned by a character.
    """

    category = serializers.SerializerMethodField()

    class Meta:
        model = Tool
        fields = ["id", "name", "weight", "category"]

    @staticmethod
    def get_category(obj):
        return obj.get_category_display()


class CharacterWeaponSerializer(serializers.ModelSerializer):
    """
    Serialize details of the weapon owned by the character and whether it is donned/equipped.
    """

    id = serializers.CharField(source="weapon.id")
    name = serializers.CharField(source="weapon.name")
    weight = serializers.CharField(source="weapon.weight")
    weapon_type = serializers.SerializerMethodField()
    damage = serializers.SerializerMethodField()
    damage_type = serializers.SerializerMethodField()

    class Meta:
        model = CharacterWeapon
        fields = ["id", "name", "weight", "equipped", "weapon_type", "damage", "damage_type"]

    @staticmethod
    def get_weapon_type(obj):
        return obj.weapon.get_weapon_type_display()

    @staticmethod
    def get_damage(obj):
        return obj.weapon.damage()

    @staticmethod
    def get_damage_type(obj):
        return obj.weapon.get_damage_type_display()


class EquipmentPackSerializer(serializers.ModelSerializer):
    """
    Serialize EquipmentPack objects for the list view.
    """

    class Meta:
        model = EquipmentPack
        exclude = ["gear"]


class EquipmentPackGearSerializer(serializers.ModelSerializer):
    """
    How many of which AdventuringGear is assigned to EquipmentPack.
    The id of the m2m entry is not important, so overriding id with the id of the AdventuringGear
    object to conform to other name-and-id conventions.
    """

    id = serializers.CharField(source="adventuring_gear_id")  # return id of AdventuringGear object
    name = serializers.CharField(source="adventuring_gear.name")

    class Meta:
        model = EquipmentPackGear
        fields = ["id", "quantity", "name"]


class EquipmentPackDetailSerializer(serializers.ModelSerializer):
    """
    Serialize details of an EquipmentPack object with included AdventuringGear.
    """

    gear = EquipmentPackGearSerializer(many=True, source="equipmentpackgear_set")

    class Meta:
        model = EquipmentPack
        fields = "__all__"


class ToolNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tool
        fields = ["id", "name"]


class ToolSerializer(serializers.ModelSerializer):
    """
    Serialize Tool object for detail and list views.
    """

    category = serializers.SerializerMethodField()

    class Meta:
        model = Tool
        fields = "__all__"

    @staticmethod
    def get_category(obj):
        return obj.get_category_display()


class WeaponNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Weapon
        fields = ["id", "name"]


class WeaponSerializer(serializers.ModelSerializer):
    """
    Serialize Weapon objects for detail and list views.
    """

    weapon_type = serializers.SerializerMethodField()

    class Meta:
        model = Weapon
        fields = "__all__"

    @staticmethod
    def get_weapon_type(obj):
        return obj.get_weapon_type_display()
