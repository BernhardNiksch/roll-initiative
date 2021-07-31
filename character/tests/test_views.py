from django.test import TestCase
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from campaign.models import Campaign
from character.models import CharacterClass, CharacterRace, Character


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

    def pagination_tester(self, url, page_size, result_count):
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], result_count)
        self.assertEqual(len(response.data["results"]), response.data["count"])
        self.assertIsNone(response.data.get("previous"))
        self.assertIsNone(response.data.get("next"))
        expected_first_result = response.data["results"][0]
        next_expected_first_result = response.data["results"][page_size]

        response = self.client.post(f"{url}?page_size={page_size}")
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
        response = self.client.post(f"{url}{next_link}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], result_count)
        self.assertIsNone(response.data.get("next"))
        self.assertEqual(len(response.data["results"]), page_2_size)
        self.assertEqual(response.data["results"][0], next_expected_first_result)
        previous_link = response.data["previous"]

        response = self.client.post(f"{url}{previous_link}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0], expected_first_result)

    def search_results(self, search, url, result_count):
        data = {"search": search}
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
        self.pagination_tester(url, page_size, result_count)

    def test_character_class_list_search(self):
        """
        Test that the character class list is searchable.

        The character class list is searchable on the class' name.
        The response should contain only matching results.
        """

        url = "/api/character/class/list/"

        results = self.search_results("bar", url, 2)  # This should find Bard and Barbarian
        self.assertEqual(results[0]["name"], "Barbarian")
        self.assertEqual(results[1]["name"], "Bard")

        results = self.search_results("ter", url, 1)  # This should find Fighter
        self.assertEqual(results[0]["name"], "Fighter")

    # TODO not sure why, but the dynamic fields of the ManagedListSerializer do not work in testing.
    # def test_character_class_list_sorting(self):
    #     """
    #     Test that the character class list is searchable.
    #
    #     The character class list is searchable on the class' name.
    #     The response should contain only matching results.
    #     """
    #
    #     url = "/api/character/class/list/"
    #
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 200)
    #     default_order = response.data["results"]
    #
    #     # By default, the class list is sorted by name.
    #     data = {"sort": {"name": True}}  # Should return same as default order
    #     response = self.client.post(url, data=data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data["results"], default_order)
    #
    #     data = {"sort": {"name": False}}  # Should reverse the default order
    #     response = self.client.post(url, data=data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data["results"], list(reversed(default_order)))
    #
    #     data = {"sort": {"hit_die": True}}
    #     response = self.client.post(url, data=data)
    #     self.assertEqual(response.status_code, 200)
    #     # self.assertNotEqual(response.data["results"], default_order)
    #     hit_die = [cc["hit_die"] for cc in response.data["results"]]
    #     self.assertEqual(hit_die, sorted(hit_die))
    #
    #     data = {"sort": {"hit_die": False}}
    #     response = self.client.post(url, data=data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotEqual(response.data["results"], default_order)
    #     hit_die = [cc["hit_die"] for cc in response.data["results"]]
    #     self.assertEqual(hit_die, sorted(hit_die, reverse=True))

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
        self.pagination_tester(url, page_size, result_count)

    def test_character_race_list_search(self):
        """
        Test that the character race list is searchable.

        The character race list is searchable on the race's name.
        The response should contain only matching results.
        """

        url = "/api/character/race/list/"

        results = self.search_results("F", url, 2)
        self.assertEqual(results[0]["name"], "Dwarf")
        self.assertEqual(results[1]["name"], "Elf")

        results = self.search_results("hom", url, 1)
        self.assertEqual(results[0]["name"], "Homo Sapiens")

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
        self.pagination_tester(url, page_size, result_count)

    def test_character_list_search(self):
        """
        Test that the character list is searchable.

        The character class list is searchable on the first_name, last_name, title, race__name,
        and character_class__name.
        The response should contain only matching results.
        """

        url = "/api/character/list/"

        # Search title
        results = self.search_results("bruh", url, 1)
        self.assertEqual(results[0]["title"], "Bruh")
        self.assertEqual(results[0]["first_name"], "Stevey")

        # Search first_name
        results = self.search_results("Gerold", url, 1)
        self.assertEqual(results[0]["title"], "mister")
        self.assertEqual(results[0]["first_name"], "Gerold")

        # Search last_name
        results = self.search_results("odson", url, 1)
        self.assertEqual(results[0]["first_name"], "Glod")
        self.assertEqual(results[0]["last_name"], "Glodson")

        # Search character class
        results = self.search_results("fight", url, 1)
        self.assertEqual(results[0]["first_name"], "Stevey")
        self.assertEqual(results[0]["character_class"]["name"], "Fighter")

        # Search character race
        results = self.search_results("Dwa", url, 1)
        self.assertEqual(results[0]["first_name"], "Glod")
        self.assertEqual(results[0]["race"]["name"], "Dwarf")

        # Search across fields
        results = self.search_results("ter", url, 2)
        self.assertEqual(results[0]["first_name"], "Gerold")
        self.assertEqual(results[0]["title"], "mister")
        self.assertEqual(results[1]["first_name"], "Stevey")
        self.assertEqual(results[1]["character_class"]["name"], "Fighter")

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
