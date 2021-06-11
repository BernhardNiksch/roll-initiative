import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.models import DamageMixin, MoneyMixin


class Armor(models.Model):
    """
    Static table of protective armor.

    armor_class specifies the character's base AC while wearing the armor.
    armor_class_increase, on the other hand, is a modifier for armor such as shields which add to
    the character's AC.

    All armor is priced in gold and does not require the additional coinage included in
    MoneyMixin. This choice might be reconsidered if MoneyMixin gets some useful methods.
    """

    LIGHT = "LIGHT"
    MEDIUM = "MEDIUM"
    HEAVY = "HEAVY"
    SHIELD = "SHIELD"
    ARMOR_TYPE_CHOICES = (
        (LIGHT, "Light Armor"),
        (MEDIUM, "Medium Armor"),
        (HEAVY, "Heavy Armor"),
        (SHIELD, "Shield"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=20, unique=True)
    armor_type = models.CharField(choices=ARMOR_TYPE_CHOICES, max_length=10)
    gold = models.PositiveSmallIntegerField()
    armor_class = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(20)]
    )
    armor_class_increase = models.PositiveSmallIntegerField(default=0)
    dex_modifier_max = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(10)]
    )
    strength_requirement = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(20)]
    )
    stealth_disadvantage = models.BooleanField(default=False)
    weight = models.DecimalField(decimal_places=2, max_digits=4)

    class Meta:
        db_table = "armor"
        ordering = ("armor_type", "name")

    def __str__(self):
        return f"{self.name} ({self.get_armor_type_display()})"


class CharacterArmor(models.Model):
    """
    Many-to-many table of armor owned and worn by a character.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey("character.Character", models.CASCADE)
    armor = models.ForeignKey("Armor", models.PROTECT)
    equipped = models.BooleanField()

    class Meta:
        db_table = "character_armor"

    def __str__(self):
        return f"{self.character} - {self.armor.name}"


class Weapon(MoneyMixin, DamageMixin):
    """
    Static table of all things with which to smack some monsters (except improvised weapons, of
    course).
    """

    SIMPLE_MELEE = "SIMPLE_MELEE"
    SIMPLE_RANGED = "SIMPLE_RANGED"
    MARTIAL_MELEE = "MARTIAL_MELEE"
    MARTIAL_RANGED = "MARTIAL_RANGED"
    WEAPON_TYPE_CHOICES = (
        (SIMPLE_MELEE, "Simple Melee Weapon"),
        (SIMPLE_RANGED, "Simple Ranged Weapon"),
        (MARTIAL_MELEE, "Martial Melee Weapon"),
        (MARTIAL_RANGED, "Martial Ranged Weapon"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30, unique=True)
    weapon_type = models.CharField(choices=WEAPON_TYPE_CHOICES, max_length=15)
    weight = models.DecimalField(decimal_places=2, max_digits=4, default=0)

    # Weapon properties
    normal_range = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(200)], null=True, blank=True,
    )
    maximum_range = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(1000)], null=True, blank=True,
    )
    ammunition = models.BooleanField(default=False)
    finesse = models.BooleanField(default=False)
    heavy = models.BooleanField(default=False)
    light = models.BooleanField(default=False)
    loading = models.BooleanField(default=False)
    reach = models.BooleanField(default=False)
    special = models.BooleanField(default=False)
    thrown = models.BooleanField(default=False)
    two_handed = models.BooleanField(default=False)
    versatile = models.BooleanField(default=False)

    class Meta:
        db_table = "weapon"
        ordering = ("weapon_type", "name")

    def __str__(self):
        return f"{self.name} ({self.get_weapon_type_display()})"


class CharacterWeapon(models.Model):
    """
    Many-to-many table of weapons owned and equipped by a character.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey("character.Character", models.CASCADE)
    weapon = models.ForeignKey("Weapon", models.PROTECT)
    equipped = models.BooleanField()

    class Meta:
        db_table = "character_weapon"

    def __str__(self):
        return f"{self.character} - {self.weapon.name}"


class AdventuringGear(MoneyMixin):
    """
    Static normalised table for adventuring gear.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30)
    weight = models.DecimalField(decimal_places=2, max_digits=4)
    description = models.TextField()
    length = models.PositiveSmallIntegerField(null=True, blank=True)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "adventuring_gear"
        ordering = ("name",)

    def __str__(self):
        return self.name


class CharacterAdventuringGear(models.Model):
    """
    Many-to-many table to manage gear assigned to the character and keep track of the length or
    quantity left.

    The table can be kept on the smaller side by limiting entries to one per character per item
    type, adjusting the weight and length or quantity as items are bought or used.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    character = models.ForeignKey("character.Character", models.CASCADE)
    adventuring_gear = models.ForeignKey("AdventuringGear", models.PROTECT)
    length = models.PositiveSmallIntegerField(null=True, blank=True)
    quantity = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "character_adventuring_gear"

    def __str__(self):
        return f"{self.character} - {self.adventuring_gear.name}"

    def weight(self):
        if self.adventuring_gear.weight:
            if self.adventuring_gear.length:
                ratio = self.length / self.adventuring_gear.length
            else:
                ratio = self.quantity / self.adventuring_gear.quantity
            weight = float(self.adventuring_gear.weight) * ratio
            return f"{weight:.2f}"
        return "0.00"


class EquipmentPack(models.Model):
    """
    Static table to manage backpacks and chests pre-packed with adventuring gear goodies.

    Equipment packs are all priced in gold and do not require the additional coinage included in
    MoneyMixin. This choice might be reconsidered if MoneyMixin gets some useful methods.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    gold = models.PositiveSmallIntegerField()
    gear = models.ManyToManyField(
        AdventuringGear, related_name="equipment_pack", through="EquipmentPackGear"
    )

    class Meta:
        db_table = "equipment_pack"
        ordering = ("name",)

    def __str__(self):
        return self.name


class EquipmentPackGear(models.Model):
    """
    Many-to-many table to model the adventuring gear contents of an equipment pack.

    Quantity specifies the amount of the type of gear included in the pack. For instance, sheets of
    paper are bought individually and modeled in AdventuringGear as single sheets, but a Diplomat's
    Pack contains 5 sheets of paper.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    equipment_pack = models.ForeignKey(EquipmentPack, on_delete=models.CASCADE)
    adventuring_gear = models.ForeignKey(AdventuringGear, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "equipment_pack_gear"

    def __str__(self):
        return f"{self.equipment_pack} - {self.adventuring_gear}"


class Tool(MoneyMixin):
    """
    Static table of specialised tools for crafting, forging, repairing, breaking, musicing, etc.
    """

    ARTISANS_TOOLS = "ARTISANS_TOOLS"
    GAMING_SET = "GAMING_SET"
    MUSICAL_INSTRUMENT = "MUSICAL_INSTRUMENT"
    TOOL_CATEGORY_CHOICES = (
        (ARTISANS_TOOLS, "Artisan's Tools"),
        (GAMING_SET, "Gaming Set"),
        (MUSICAL_INSTRUMENT, "Musical Instrument"),
        (None, "Other")
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    category = models.CharField(
        max_length=20, choices=TOOL_CATEGORY_CHOICES, default=None, null=True, blank=True
    )
    name = models.CharField(max_length=30)
    weight = models.DecimalField(decimal_places=2, max_digits=4)
    description = models.TextField()

    class Meta:
        db_table = "tool"
        ordering = ("name",)

    def __str__(self):
        return self.name
