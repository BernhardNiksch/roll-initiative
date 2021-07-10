import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common import abilities
from common.helpers import roll
from common.models import AbilityScoreHealthMixin, CampaignManagementMixin, MoneyMixin
from equipment.models import Armor, Weapon


class CharacterRace(models.Model):
    """Class to model different character races."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    speed = models.PositiveSmallIntegerField(validators=[MaxValueValidator(50)])
    strength_increase = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(-10), MaxValueValidator(10)]
    )
    dexterity_increase = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(-10), MaxValueValidator(10)]
    )
    constitution_increase = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(-10), MaxValueValidator(10)]
    )
    intelligence_increase = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(-10), MaxValueValidator(10)]
    )
    wisdom_increase = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(-10), MaxValueValidator(10)]
    )
    charisma_increase = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(-10), MaxValueValidator(10)]
    )
    languages = ArrayField(base_field=models.CharField(max_length=20), null=True)

    class Meta:
        db_table = "character_race"
        ordering = ("name", )

    def __str__(self):
        return self.name


class CharacterClass(models.Model):
    """Class to model different character classes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    hit_die = models.PositiveSmallIntegerField()
    primary_abilities = ArrayField(
        models.CharField(choices=abilities.ABILITY_CHOICES, max_length=15)
    )
    saving_throw_proficiencies = ArrayField(
        models.CharField(choices=abilities.ABILITY_CHOICES, max_length=15)
    )
    armor_proficiencies = models.ManyToManyField(Armor, blank=True)
    weapon_proficiencies = models.ManyToManyField(Weapon, blank=True)
    tool_proficiencies = models.ManyToManyField("equipment.Tool", blank=True)
    features = models.ManyToManyField(
        "features.Feat", through="features.CharacterClassFeature", blank=True
    )

    class Meta:
        db_table = "character_class"
        ordering = ("name", )

    def __str__(self):
        return self.name


class Character(AbilityScoreHealthMixin, CampaignManagementMixin, MoneyMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)
    age = models.PositiveSmallIntegerField()
    race = models.ForeignKey("CharacterRace", on_delete=models.PROTECT)
    character_class = models.ForeignKey("CharacterClass", on_delete=models.PROTECT)
    level = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    experience_points = models.PositiveIntegerField(default=0)
    languages = ArrayField(base_field=models.CharField(max_length=20), null=True)
    feats = models.ManyToManyField("features.Feat", through="features.CharacterFeat", blank=True)
    armor = models.ManyToManyField(
        "equipment.Armor", through="equipment.CharacterArmor", blank=True
    )
    weapons = models.ManyToManyField(
        "equipment.Weapon", through="equipment.CharacterWeapon", blank=True
    )
    adventuring_gear = models.ManyToManyField(
        "equipment.AdventuringGear",
        through="equipment.CharacterAdventuringGear",
        blank=True,
        related_name="character",
    )
    tools = models.ManyToManyField("equipment.Tool", blank=True)

    class Meta:
        db_table = "character"
        ordering = ("first_name", "last_name", "race", "level")

    def __str__(self):
        names = [self.title, self.first_name, self.last_name]
        return " ".join([n for n in names if n])

    def grow_older(self, years=1):
        self.age = self.age + years

    def level_up(self, max_hp_increase):
        self.level = self.level + 1
        self.increase_max_hp(max_hp_increase, add_constitution=True)
