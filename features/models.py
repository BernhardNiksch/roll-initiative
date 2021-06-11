import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Feat(models.Model):
    """
    Static table for class features and general feats.

    Class features may be assigned to a character class to be inherited by the character at certain
    levels.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30)
    prerequisite = models.CharField(max_length=50, blank=True)
    description = models.TextField()

    class Meta:
        db_table = "feat"
        ordering = ("name",)

    def __str__(self):
        return self.name


class CharacterClassFeature(models.Model):
    """
    Many-to-many table to manage class features gained by at each level.
    """

    feat = models.ForeignKey("Feat", models.PROTECT)
    character_class = models.ForeignKey("character.CharacterClass", models.CASCADE)
    level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )

    class Meta:
        db_table = "character_class_feature"

    def __str__(self):
        return f"{self.character_class} - {self.feat}"


class CharacterFeat(models.Model):
    """
    Many-to-many table to manage feats and class features assigned to a character.

    Using a through table to later link an ability score adjustment to an assigned feature.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    feat = models.ForeignKey("Feat", models.PROTECT)
    character = models.ForeignKey("character.Character", models.CASCADE)

    class Meta:
        db_table = "character_feat"

    def __str__(self):
        return f"{self.character} - {self.feat}"
