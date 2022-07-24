from unittest.mock import patch
from urllib.parse import urlencode

from django.test import TestCase
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from campaign.models import Campaign
from character.models import CharacterClass, CharacterRace, Character
from character.views import CharacterClassListView, CharacterRaceListView, CharacterListView
from common.helpers import result_values_for_field


class TestCharacterViews(TestCase):
    fixtures = [
        "campaign/fixtures/campaign.json",
        "character/fixtures/character.json",
        "equipment/fixtures/equipment.json",
        "features/fixtures/features.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.bard = CharacterClass.objects.get(name="Bard")
        cls.elf = CharacterRace.objects.get(name="Elf")
        cls.campaign = Campaign.objects.get(name="Campaign 2")
        cls.base_url = "/api/character/"
        cls.character_data = {
            "character_class": cls.bard.id,
            "race": cls.elf.id,
            "campaign": cls.campaign.id,
            "max_hp": 35,
            "current_hp": 28,
            "armor_class": 12,
            "strength": 9,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 10,
            "wisdom": 11,
            "charisma": 14,
            "backstory": "",
            "gold": 15,
            "title": "Sire",
            "first_name": "Elvish",
            "last_name": "Presley",
            "age": 65,
            "level": 3,
            "experience_points": 1200,
            "languages": ["Common", "Elvish"],
        }

    def create_character(self, data: dict = None):
        data = data or {}
        character_data = {
            **self.character_data,
            "campaign": self.campaign,
            "character_class": self.bard,
            "race": self.elf,
            **data,
        }
        character = Character(**character_data)
        character.save()
        return character, character_data

    def pagination_tester(self, url, page_size, result_count, list_api_view=False):
        if not list_api_view:
            response = self.client.post(url)
        else:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], result_count)
        self.assertEqual(len(response.data["results"]), response.data["count"])
        self.assertIsNone(response.data.get("previous"))
        self.assertIsNone(response.data.get("next"))
        expected_first_result = response.data["results"][0]
        next_expected_first_result = response.data["results"][page_size]

        if not list_api_view:
            response = self.client.post(f"{url}?page_size={page_size}")
        else:
            response = self.client.get(f"{url}?page_size={page_size}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], result_count)
        self.assertIsNone(response.data.get("previous"))
        self.assertEqual(len(response.data["results"]), page_size)
        self.assertEqual(response.data["results"][0], expected_first_result)
        next_link = response.data["next"]

        page_2_size = page_size
        if result_count < page_size * 2:
            page_2_size = result_count % page_size
            # Check that the second page is the right size if there aren't enough records for
            # a full page.

        if not list_api_view:
            response = self.client.post(f"{url}{next_link}")
        else:
            response = self.client.get(next_link)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], result_count)
        self.assertIsNone(response.data.get("next"))
        self.assertEqual(len(response.data["results"]), page_2_size)
        self.assertEqual(response.data["results"][0], next_expected_first_result)
        previous_link = response.data["previous"]

        if not list_api_view:
            response = self.client.post(f"{url}{previous_link}")
        else:
            response = self.client.get(previous_link)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0], expected_first_result)

    def ordering_tester(self, url, fields, default_field):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        default_order = [result[default_field] for result in response.data["results"]]
        self.assertEqual(default_order, sorted(default_order))

        for field in fields:
            data = {"ordering": field}
            response = self.client.get(f"{url}?{urlencode(data)}")
            self.assertEqual(response.status_code, 200)
            # self.assertNotEqual(response.data["results"], default_order)
            forward_order = result_values_for_field(response.data["results"], field)
            self.assertEqual(forward_order, sorted(forward_order))

            data = {"ordering": f"-{field}"}
            response = self.client.get(f"{url}?{urlencode(data)}")
            self.assertEqual(response.status_code, 200)
            backward_order = result_values_for_field(response.data["results"], field)
            self.assertEqual(backward_order, list(reversed(forward_order)))

    def search_results(self, search, url, result_count, list_api_view=False):
        data = {"search": search}
        if list_api_view:
            params = urlencode(data)
            response = self.client.get(f"{url}?{params}")
        else:
            response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], result_count)
        self.assertEqual(len(response.data["results"]), result_count)
        self.assertIsNone(response.data.get("previous"))
        self.assertIsNone(response.data.get("next"))
        return response.data["results"]

    def test_character_class_list_pagination(self):
        url = "/api/character/class/list/"
        page_size = 2
        result_count = 4
        self.pagination_tester(url, page_size, result_count, list_api_view=True)

    def test_character_class_list_search(self):
        """
        Test that the character class list is searchable.

        The character class list is searchable on the class' name.
        The response should contain only matching results.
        """

        url = "/api/character/class/list/"

        results = self.search_results("bar", url, 2, True)  # This should find Bard and Barbarian
        self.assertEqual(results[0]["name"], "Barbarian")
        self.assertEqual(results[1]["name"], "Bard")

        results = self.search_results("ter", url, 1, True)  # This should find Fighter
        self.assertEqual(results[0]["name"], "Fighter")

    def test_character_class_list_sorting(self):
        """
        Test that the character class list can be sorted/ordered.
        """

        url = "/api/character/class/list/"
        ordering_fields = CharacterClassListView.ordering_fields
        default_ordering_field = CharacterClassListView.ordering[0]
        self.ordering_tester(url, ordering_fields, default_ordering_field)

    def test_character_class_get(self):
        """
        Test that retrieving a character class works.
        """

        pk = "ea023174-5774-4bba-ad10-8d4bcd8483b9"  # Bard
        url = f"/api/character/class/{pk}/"
        with self.assertNumQueries(5):
            response = self.client.get(url)
            self.assertEqual(response.data["name"], "Bard")
            self.assertEqual(response.data["hit_die"], 8)
            self.assertEqual(len(response.data["armor_proficiencies"]), 2)
            self.assertEqual(len(response.data["tool_proficiencies"]), 1)
            self.assertEqual(len(response.data["weapon_proficiencies"]), 4)
            self.assertEqual(len(response.data["features"]), 0)

        pk = "a65632b2-17d0-43d1-9ba9-61ee9b68e744"  # Barbarian
        url = f"/api/character/class/{pk}/"
        with self.assertNumQueries(7):
            # Prefetch on feature is not working yet, so there's a extra query per feature.
            response = self.client.get(url)
            self.assertEqual(response.data["name"], "Barbarian")
            self.assertEqual(response.data["hit_die"], 12)
            self.assertEqual(len(response.data["armor_proficiencies"]), 6)
            self.assertEqual(len(response.data["tool_proficiencies"]), 0)
            self.assertEqual(len(response.data["weapon_proficiencies"]), 5)
            self.assertEqual(len(response.data["features"]), 2)

    def test_character_race_list_pagination(self):
        url = "/api/character/race/list/"
        page_size = 2
        result_count = 3
        self.pagination_tester(url, page_size, result_count, True)

    def test_character_race_list_search(self):
        """
        Test that the character race list is searchable.

        The character race list is searchable on the race's name.
        The response should contain only matching results.
        """

        url = "/api/character/race/list/"

        results = self.search_results("F", url, 2, True)
        self.assertEqual(results[0]["name"], "Dwarf")
        self.assertEqual(results[1]["name"], "Elf")

        results = self.search_results("hom", url, 1, True)
        self.assertEqual(results[0]["name"], "Homo Sapiens")

    def test_character_race_list_sorting(self):
        """
        Test that the character class list can be sorted/ordered.
        """

        url = "/api/character/race/list/"
        ordering_fields = CharacterRaceListView.ordering_fields
        default_ordering_field = CharacterRaceListView.ordering[0]
        self.ordering_tester(url, ordering_fields, default_ordering_field)

    def test_character_race_get(self):
        """
        Test that retrieving a character race works.
        """

        pk = "50d6fd1c-052e-4ed6-8473-ec55a4920770"  # Dwarf
        url = f"/api/character/race/{pk}/"
        with self.assertNumQueries(1):
            response = self.client.get(url)
            self.assertEqual(response.data["name"], "Dwarf")
            self.assertEqual(response.data["description"], "Short and stout.")
            self.assertEqual(response.data["speed"], 25)
            self.assertEqual(response.data["strength_increase"], 2)
            self.assertEqual(response.data["dexterity_increase"], 0)
            self.assertEqual(response.data["constitution_increase"], 1)
            self.assertEqual(response.data["languages"], ["English", "Dwarvish"])

        pk = "3d1b90d2-4a2f-4556-98b0-8a3c851944a6"  # Elf
        url = f"/api/character/race/{pk}/"
        with self.assertNumQueries(1):
            response = self.client.get(url)
            self.assertEqual(response.data["name"], "Elf")
            self.assertEqual(response.data["description"], "Tall-ish folk with pointy ears.")
            self.assertEqual(response.data["speed"], 30)
            self.assertEqual(response.data["strength_increase"], 0)
            self.assertEqual(response.data["dexterity_increase"], 2)
            self.assertEqual(response.data["constitution_increase"], 0)
            self.assertEqual(response.data["languages"], ["English", "Elvish"])

    def test_character_list_pagination(self):
        url = "/api/character/list/"
        page_size = 2
        result_count = 3
        self.pagination_tester(url, page_size, result_count, True)

    def test_character_list_search(self):
        """
        Test that the character list is searchable.

        The character class list is searchable on the first_name, last_name, title, race__name,
        and character_class__name.
        The response should contain only matching results.
        """

        url = "/api/character/list/"

        # Search title
        results = self.search_results("bruh", url, 1, True)
        self.assertEqual(results[0]["title"], "Bruh")
        self.assertEqual(results[0]["first_name"], "Stevey")

        # Search first_name
        results = self.search_results("Gerold", url, 1, True)
        self.assertEqual(results[0]["title"], "mister")
        self.assertEqual(results[0]["first_name"], "Gerold")

        # Search last_name
        results = self.search_results("odson", url, 1, True)
        self.assertEqual(results[0]["first_name"], "Glod")
        self.assertEqual(results[0]["last_name"], "Glodson")

        # Search character class
        results = self.search_results("fight", url, 1, True)
        self.assertEqual(results[0]["first_name"], "Stevey")
        self.assertEqual(results[0]["character_class"]["name"], "Fighter")

        # Search character race
        results = self.search_results("Dwa", url, 1, True)
        self.assertEqual(results[0]["first_name"], "Glod")
        self.assertEqual(results[0]["race"]["name"], "Dwarf")

        # Search across fields
        results = self.search_results("ter", url, 2, True)
        self.assertEqual(results[0]["first_name"], "Gerold")
        self.assertEqual(results[0]["title"], "mister")
        self.assertEqual(results[1]["first_name"], "Stevey")
        self.assertEqual(results[1]["character_class"]["name"], "Fighter")

    def test_character_list_sorting(self):
        """
        Test that the character class list can be sorted/ordered.
        """

        url = "/api/character/list/"
        ordering_fields = CharacterListView.ordering_fields
        default_ordering_field = CharacterListView.ordering[0]
        self.ordering_tester(url, ordering_fields, default_ordering_field)

    def test_character_get(self):
        """
        Test that retrieving a character works.
        """

        pk = "de1ec576-8aa9-4892-bfe5-e6193166a222"  # mister Gerold
        url = f"{self.base_url}{pk}/"
        with self.assertNumQueries(2):
            response = self.client.get(url)
            self.assertEqual(response.data["title"], "mister")
            self.assertEqual(response.data["first_name"], "Gerold")
            self.assertEqual(response.data["max_hp"], 8)
            self.assertEqual(response.data["current_hp"], 6)
            self.assertEqual(response.data["armor_class"], 11)
            self.assertEqual(response.data["dexterity"], 14)
            self.assertEqual(response.data["constitution"], 10)
            self.assertEqual(response.data["languages"], ["Common", "Elvish"])
            self.assertEqual(response.data["race"]["name"], "Elf")
            self.assertEqual(response.data["character_class"]["name"], "Ranger")
            self.assertEqual(response.data["campaign"]["name"], "My first campaign")

    def test_character_get_404(self):
        """Test that 404 is returned if the character does not exist."""

        pk = "65083c70-8adb-42d2-9024-3890cdf03841"  # Random uuid. Character shouldn't exist.
        url = f"{self.base_url}{pk}/"
        with self.assertNumQueries(1):
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_character_add(self):
        character_data = self.character_data
        with self.assertNumQueries(4):
            response = self.client.post(self.base_url, data=self.character_data)
            self.assertEqual(response.status_code, HTTP_201_CREATED)
            self.assertEqual(response.data["title"], character_data["title"])
        character = Character.objects.get(first_name="Elvish", last_name="Presley")
        self.assertEqual(character.character_class, self.bard)
        self.assertEqual(character.race, self.elf)
        self.assertEqual(character.campaign, self.campaign)
        self.assertEqual(character.age, character_data["age"])
        self.assertEqual(character.current_hp, character_data["current_hp"])
        self.assertEqual(character.last_name, character_data["last_name"])
        self.assertEqual(character.dexterity, character_data["dexterity"])
        self.assertEqual(character.level, character_data["level"])
        self.assertEqual(character.experience_points, character_data["experience_points"])
        character.delete()

    def test_character_add_default_values(self):
        character_data = self.character_data.copy()
        character_data.pop("level")
        character_data.pop("experience_points")
        with self.assertNumQueries(4):
            response = self.client.post(self.base_url, data=character_data)
            self.assertEqual(response.status_code, HTTP_201_CREATED)
            self.assertEqual(response.data["title"], character_data["title"])
        character = Character.objects.get(first_name="Elvish", last_name="Presley")
        self.assertEqual(character.level, 1)
        self.assertEqual(character.experience_points, 0)
        self.assertEqual(character.temporary_hp, 0)
        character.delete()

    def test_character_delete(self):
        character, character_data = self.create_character()
        url = f"{self.base_url}{character.id}/"
        with self.assertNumQueries(7):
            response = self.client.delete(url)
            self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
        with self.assertRaises(Character.DoesNotExist):
            character.refresh_from_db()

    def test_character_delete_404(self):
        """Test that 404 is returned when deleting a character that does not exist."""

        pk = "65083c70-8adb-42d2-9024-3890cdf03841"  # Random uuid. Character shouldn't exist.
        url = f"{self.base_url}{pk}/"
        with self.assertNumQueries(1):
            response = self.client.delete(url)
            self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_character_health_get(self):
        pk = "de1ec576-8aa9-4892-bfe5-e6193166a222"  # mister Gerold
        url = f"{self.base_url}{pk}/hit-points/"
        with self.assertNumQueries(1):
            response = self.client.get(url)
            self.assertEqual(response.data["current_hp"], 6)
            self.assertEqual(response.data["max_hp"], 8)
            self.assertEqual(response.data["temporary_hp"], 0)

    def test_character_health_update(self):
        character, character_data = self.create_character()
        url = f"{self.base_url}{character.id}/hit-points/"

        data = {
            "current_hp": 10,
            "max_hp": 12,
            "temporary_hp": 3,
        }
        with self.assertNumQueries(2):
            response = self.client.put(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
        character.refresh_from_db()
        self.assertEqual(character.current_hp, 10)
        self.assertEqual(character.max_hp, 12)
        self.assertEqual(character.temporary_hp, 3)

        data = {
            "current_hp": 6,
            "max_hp": 8,
            "temporary_hp": 0,
        }
        with self.assertNumQueries(2):
            response = self.client.put(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
            self.assertEqual(response.data["current_hp"], 6)
            self.assertEqual(response.data["max_hp"], 8)
            self.assertEqual(response.data["temporary_hp"], 0)
        character.refresh_from_db()
        self.assertEqual(character.current_hp, 6)
        self.assertEqual(character.max_hp, 8)
        self.assertEqual(character.temporary_hp, 0)

        character.delete()

    def test_character_health_partial_update(self):
        character, character_data = self.create_character({"temporary_hp": 1})
        url = f"{self.base_url}{character.id}/hit-points/"

        data = {"current_hp": 12}
        with self.assertNumQueries(2):
            response = self.client.patch(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
            self.assertEqual(response.data["current_hp"], 12)
            self.assertEqual(response.data["max_hp"], character_data["max_hp"])
            self.assertEqual(response.data["temporary_hp"], character_data["temporary_hp"])
        character.refresh_from_db()
        self.assertEqual(character.current_hp, 12)
        self.assertEqual(character.max_hp, character_data["max_hp"])
        self.assertEqual(character.temporary_hp, character_data["temporary_hp"])

        data = {
            "max_hp": 18,
            "temporary_hp": 3,
        }
        with self.assertNumQueries(2):
            response = self.client.patch(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
            self.assertEqual(response.data["current_hp"], 12)
            self.assertEqual(response.data["max_hp"], 18)
            self.assertEqual(response.data["temporary_hp"], 3)
        character.refresh_from_db()
        self.assertEqual(character.current_hp, 12)
        self.assertEqual(character.max_hp, 18)
        self.assertEqual(character.temporary_hp, 3)

        data = {
            "current_hp": 6,
            "max_hp": 8,
            "temporary_hp": 0,
        }
        with self.assertNumQueries(2):
            response = self.client.patch(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
            self.assertEqual(response.data["current_hp"], 6)
            self.assertEqual(response.data["max_hp"], 8)
            self.assertEqual(response.data["temporary_hp"], 0)
        character.refresh_from_db()
        self.assertEqual(character.current_hp, 6)
        self.assertEqual(character.max_hp, 8)
        self.assertEqual(character.temporary_hp, 0)

        character.delete()

    def test_character_health_update_validate_current_hp_less_than_max(self):
        character, character_data = self.create_character()
        url = f"{self.base_url}{character.id}/hit-points/"
        self.assertTrue(character.current_hp > 0, "Test requires current HP greater than 0.")

        payloads = (
            {"max_hp": character.current_hp - 1},
            {"current_hp": character.max_hp + 1},
            {"current_hp": 13, "max_hp": 9}
        )
        for data in payloads:
            current_hp = data.get("current_hp", character.current_hp)
            max_hp = data.get("max_hp", character.max_hp)
            response = self.client.patch(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.data["non_field_errors"][0],
                f"The current HP ({current_hp}) may not exceed the maximum HP ({max_hp}).",
            )
        character.delete()

    @patch("character.models.Character.adjust_temporary_hp")
    @patch("character.models.Character.heal")
    @patch("character.models.Character.increase_max_hp")
    def test_character_health_adjust(self, mock_max_hp, mock_heal, mock_temporary_hp):
        character, character_data = self.create_character()
        url = f"{self.base_url}{character.id}/hit-points/"

        data = {"current_hp": 2}
        with self.assertNumQueries(2):
            response = self.client.post(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
        mock_heal.assert_called_with(2)
        mock_temporary_hp.assert_not_called()
        mock_max_hp.assert_not_called()

        mock_heal.reset_mock()
        mock_temporary_hp.reset_mock()
        mock_max_hp.reset_mock()

        data = {"max_hp": 5}
        with self.assertNumQueries(2):
            response = self.client.post(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
        mock_max_hp.assert_called_with(5, add_constitution=False)
        mock_heal.assert_not_called()
        mock_temporary_hp.assert_not_called()

        mock_heal.reset_mock()
        mock_temporary_hp.reset_mock()
        mock_max_hp.reset_mock()

        data = {"add_constitution_to_max_hp": True, "temporary_hp": 4}
        with self.assertNumQueries(2):
            response = self.client.post(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
        mock_max_hp.assert_called_with(0, add_constitution=True)
        mock_temporary_hp.assert_called_with(4)
        mock_heal.assert_not_called()

        mock_heal.reset_mock()
        mock_temporary_hp.reset_mock()
        mock_max_hp.reset_mock()

        data = {"max_hp": -3, "add_constitution_to_max_hp": True}
        with self.assertNumQueries(2):
            response = self.client.post(url, data=data, content_type="application/json")
            self.assertEqual(response.status_code, HTTP_200_OK)
        mock_max_hp.assert_called_with(-3, add_constitution=True)
        mock_heal.assert_not_called()
        mock_temporary_hp.assert_not_called()
