from unittest.mock import Mock, patch

from django.db import IntegrityError
from django.test import TestCase

from character.models import CharacterClass, CharacterRace, Character
from common.abilities import WISDOM, STRENGTH


class TestCharacterClass(TestCase):
    @staticmethod
    def create_character_class(
            name, description="Test", hit_die=6, abilities=None, saving_throws=None, **kwargs
    ):
        abilities = abilities or [WISDOM]
        saving_throws = saving_throws or [STRENGTH]
        return CharacterClass.objects.create(
            name=name,
            description=description,
            hit_die=hit_die,
            primary_abilities=abilities,
            saving_throw_proficiencies=saving_throws,
            **kwargs,
        )

    def test_character_class_string(self):
        """Confirm that calling __str__() returns the object's name."""

        name = "Test class"
        klas = self.create_character_class(name)
        self.assertTrue(isinstance(klas, CharacterClass))
        self.assertEqual(str(klas), name)

    def test_unique_name(self):
        """Test that name is unique"""

        name = "Unique name"
        self.create_character_class(name)
        with self.assertRaises(IntegrityError, msg=f"Key (name)=({name}) already exists."):
            self.create_character_class(name)


class TestCharacterRace(TestCase):
    @staticmethod
    def create_character_race(name, **kwargs):
        return CharacterRace.objects.create(
            name=name,
            description="Testing",
            speed=kwargs.pop("speed", None) or 25,
            languages=kwargs.pop("speed", None) or ["English"],
            **kwargs,
        )

    def test_character_race_string(self):
        """Confirm that calling __str__() returns the object's name."""

        name = "Test race"
        race = self.create_character_race(name)
        self.assertTrue(isinstance(race, CharacterRace))
        self.assertEqual(str(race), name)

    def test_unique_name(self):
        """Test that name is unique."""

        name = "Unique name"
        self.create_character_race(name)
        with self.assertRaises(IntegrityError, msg=f"Key (name)=({name}) already exists."):
            self.create_character_race(name)

    def test_ability_score_increase_defaults(self):
        """Test the ability score increase fields and defaults."""

        ability_scores = {
            "charisma_increase": 1,
            "constitution_increase": 3,
            "dexterity_increase": 5,
            "intelligence_increase": -2,
            "strength_increase": -4,
            "wisdom_increase": -6,
        }
        increases_race = self.create_character_race(name="Increases", **ability_scores)
        for ability, increase in ability_scores.items():
            self.assertEqual(getattr(increases_race, ability), increase)

        defaults_race = self.create_character_race(name="Defaults")
        for ability in ability_scores:
            self.assertEqual(getattr(defaults_race, ability), 0)


class TestCharacter(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCharacter, self).__init__(*args, **kwargs)
        self.race = None
        self.klas = None

    def create_character(self, first_name, **kwargs):
        if not self.race:
            self.race = TestCharacterRace().create_character_race("Race")
        if not self.klas:
            self.klas = TestCharacterClass().create_character_class("Class")
        return Character.objects.create(
            # character fields
            first_name=first_name,
            age=kwargs.pop("age", 21),
            race=self.race,
            character_class=self.klas,
            languages=kwargs.pop("language", ["English"]),

            # AbilityScoreMixin Fields
            max_hp=kwargs.pop("max_hp", 22),
            current_hp=kwargs.pop("current_hp", 13),
            armor_class=kwargs.pop("armor_class", 14),
            strength=kwargs.pop("strength", 12),
            dexterity=kwargs.pop("dexterity", 12),
            constitution=kwargs.pop("constitution", 12),
            intelligence=kwargs.pop("intelligence", 12),
            wisdom=kwargs.pop("wisdom", 12),
            charisma=kwargs.pop("charisma", 12),

            **kwargs,
        )

    def test_character_string(self):
        """Confirm that calling __str__() returns the character's title, first, and last name."""

        character = self.create_character(first_name="Andy")
        self.assertTrue(isinstance(character, Character))
        self.assertEqual(str(character), "Andy")

        character = self.create_character(first_name="Susan", title="Miss")
        self.assertEqual(str(character), "Miss Susan")

        character = self.create_character(first_name="Poopy", title="Mr.", last_name="Butthole")
        self.assertEqual(str(character), "Mr. Poopy Butthole")

    def test_aging(self):
        """Test that age and grow_older() works."""

        character = self.create_character(first_name="Steve", age=18)
        self.assertEqual(character.age, 18)
        character.grow_older()
        self.assertEqual(character.age, 19)
        character.grow_older(6)
        self.assertEqual(character.age, 25)
        character.grow_older(-4)
        self.assertEqual(character.age, 21)

    def test_leveling(self):
        """Test leveling up."""

        character = self.create_character(first_name="Default Level One")
        self.assertEqual(character.level, 1)
        character.increase_max_hp = Mock()
        character.level_up(max_hp_increase=5)
        self.assertEqual(character.level, 2)
        character.increase_max_hp.assert_called_with(5, add_constitution=True)

        character = self.create_character(first_name="Level Two", level=8)
        self.assertEqual(character.level, 8)
        character.increase_max_hp = Mock()
        character.level_up(3)
        self.assertEqual(character.level, 9)
        character.increase_max_hp.assert_called_with(3, add_constitution=True)

    def test_damage(self):
        """Test whether characters can take damage."""

        character = self.create_character(first_name="Dave", max_hp=30, current_hp=30)
        self.assertEqual(character.current_hp, 30)
        character.take_damage(5)
        self.assertEqual(character.current_hp, 25)
        character.take_damage(20)
        self.assertEqual(character.current_hp, 5)
        character.take_damage(99)
        self.assertEqual(character.current_hp, 0)  # negative hp normalised to 0

    def test_healing(self):
        """Test that a character can be healed."""

        character = self.create_character(first_name="Tina", max_hp=30, current_hp=15)
        self.assertEqual(character.current_hp, 15)
        character.heal(10)
        self.assertEqual(character.current_hp, 25)
        character.heal(55)
        self.assertEqual(character.current_hp, 30)  # can't heal up to more than max_hp

    def test_healing(self):
        """Test that a character can be healed."""

        constitution = 14  # this give a modifier of 2
        character = self.create_character(
            first_name="Jean", max_hp=10, current_hp=10, constitution=constitution
        )

        # Test that a character with full HP still has full HP after HP increase.
        self.assertEqual(character.max_hp, 10)
        self.assertEqual(character.current_hp, 10)
        character.increase_max_hp(8, add_constitution=True)  # +2 constitution modifier, total 10
        self.assertEqual(character.max_hp, 20)  # Jean has a constitution of 14(+2)
        self.assertEqual(character.current_hp, 20)  # HP was full before and should be afterwards

        # Test that current HP increases proportionately to max HP, rounding up.
        # 50%
        character.current_hp = 10
        self.assertEqual(character.max_hp, 20)
        self.assertEqual(character.current_hp, 10)
        character.increase_max_hp(10)  # don't add constitution mod
        self.assertEqual(character.max_hp, 30)
        self.assertEqual(character.current_hp, 15)
        # 75%
        character.max_hp = 20
        self.assertEqual(character.max_hp, 20)
        self.assertEqual(character.current_hp, 15)
        character.increase_max_hp(13, add_constitution=True)  # +2 constitution modifier, total 15
        self.assertEqual(character.max_hp, 35)
        self.assertEqual(character.current_hp, 27)  # 15 * 0.75 = 11.25, rounded up to 12
