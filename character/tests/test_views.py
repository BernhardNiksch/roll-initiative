from django.test import TestCase


class TestCharacterViews(TestCase):
    fixtures = [
        "campaign/fixtures/campaign.json",
        "character/fixtures/character.json",
        "equipment/fixtures/equipment.json",
        "features/fixtures/features.json",
    ]

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
