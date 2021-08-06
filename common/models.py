from math import ceil

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .helpers import ability_modifier


class AbilityScoreHealthMixin(models.Model):
    max_hp = models.PositiveSmallIntegerField()
    current_hp = models.PositiveSmallIntegerField()
    temporary_hp = models.PositiveSmallIntegerField(default=0)
    armor_class = models.PositiveSmallIntegerField()
    strength = models.PositiveSmallIntegerField(validators=[MaxValueValidator(20)])
    dexterity = models.PositiveSmallIntegerField(validators=[MaxValueValidator(20)])
    constitution = models.PositiveSmallIntegerField(validators=[MaxValueValidator(20)])
    intelligence = models.PositiveSmallIntegerField(validators=[MaxValueValidator(20)])
    wisdom = models.PositiveSmallIntegerField(validators=[MaxValueValidator(20)])
    charisma = models.PositiveSmallIntegerField(validators=[MaxValueValidator(20)])

    class Meta:
        abstract = True

    def clean(self):
        if self.current_hp > self.max_hp:
            # assuming no temporary max health increase allowed
            raise ValidationError(_("Health cannot exceed max health."))

    def take_damage(self, hp: int):
        health = self.current_hp - hp
        if health < 0:
            health = 0
        self.current_hp = health

    def heal(self, hp: int):
        max_health = self.max_hp
        health = self.current_hp + hp
        if health < 0:
            # negative adjustments allowed
            health = 0
        if health > max_health:
            health = max_health
        self.current_hp = health

    def increase_max_hp(self, hp: int, add_constitution=False):
        if add_constitution:
            hp = hp + ability_modifier(self.constitution)
        old_max_health = self.max_hp
        self.max_hp = old_max_health + hp
        if self.max_hp < 0:
            # negative adjustments allowed
            self.max_hp = 0

        # determine new current health proportionate to new max health
        if old_max_health:
            # Let's not divide by 0
            self.current_hp = ceil(self.current_hp * self.max_hp / old_max_health)
        else:
            self.current_hp = self.max_hp


class CampaignManagementMixin(models.Model):
    backstory = models.TextField(blank=True)
    campaign = models.ForeignKey("campaign.Campaign", on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True


class DamageMixin(models.Model):
    """Mixin class to standardise the way weapons and actions deal damage."""

    SLASHING = "SLASHING"
    PIERCING = "PIERCING"
    BLUDGEONING = "BLUDGEONING"
    POISON = "POISON"
    ACID = "ACID"
    FIRE = "FIRE"
    COLD = "COLD"
    RADIANT = "RADIANT"
    NECROTIC = "NECROTIC"
    LIGHTNING = "LIGHTNING"
    THUNDER = "THUNDER"
    FORCE = "FORCE"
    PSYCHIC = "PSYCHIC"
    DAMAGE_TYPE_CHOICES = (
        (SLASHING, "Slashing"),
        (PIERCING, "Piercing"),
        (BLUDGEONING, "Bludgeoning"),
        (POISON, "Poison"),
        (ACID, "Acid"),
        (FIRE, "Fire"),
        (COLD, "Cold"),
        (RADIANT, "Radiant"),
        (NECROTIC, "Necrotic"),
        (LIGHTNING, "Lightning"),
        (THUNDER, "Thunder"),
        (FORCE, "Force"),
        (PSYCHIC, "Psychic"),
    )
    damage_die = models.PositiveSmallIntegerField(default=4, validators=[MaxValueValidator(20)])
    damage_die_count = models.PositiveSmallIntegerField(default=1)
    damage_type = models.CharField(max_length=12, choices=DAMAGE_TYPE_CHOICES, default=SLASHING)

    class Meta:
        abstract = True

    def damage(self):
        return f"{self.damage_die_count}d{self.damage_die}"


class MoneyMixin(models.Model):
    copper = models.PositiveSmallIntegerField(null=True, blank=True)
    silver = models.PositiveSmallIntegerField(null=True, blank=True)
    electrum = models.PositiveSmallIntegerField(null=True, blank=True)
    gold = models.PositiveSmallIntegerField(null=True, blank=True)
    platinum = models.PositiveSmallIntegerField(null=True, blank=True)

    # exchange_rates = {
    #     "copper": 1,
    #     "silver": 10,
    #     "electrum": 50,
    #     "gold": 100,
    #     "platinum": 1000,
    # }  # relative to copper

    class Meta:
        abstract = True
