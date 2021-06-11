from django.core.validators import MaxValueValidator
from django.db import models
import uuid

from common.models import AbilityScoreHealthMixin, CampaignManagementMixin, MoneyMixin


class MonsterType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30)
    armor_class = models.PositiveSmallIntegerField(default=10, validators=[MaxValueValidator(20)])
    hit_die = models.PositiveSmallIntegerField(default=4, validators=[MaxValueValidator(20)])
    hit_die_count = models.PositiveSmallIntegerField(default=1)
    strength = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(30)])
    dexterity = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(30)])
    constitution = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(30)])
    intelligence = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(30)])
    wisdom = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(30)])
    charisma = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(30)])

    class Meta:
        db_table = "monster_type"
        ordering = ("name", )

    def __str__(self):
        return self.name


class Monster(AbilityScoreHealthMixin, CampaignManagementMixin, MoneyMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    monster_type = models.ForeignKey("MonsterType", on_delete=models.PROTECT)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "monster"
        ordering = ("first_name", "last_name")

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()
