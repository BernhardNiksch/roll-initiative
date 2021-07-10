from django.db import IntegrityError
from django.test import TestCase

from character.models import CharacterClass
from common.abilities import WISDOM, STRENGTH


class TestCharacterViews(TestCase):
    fixtures = [
        "campaign/fixtures/campaign.json",
        "character/fixtures/character.json",
        "equipment/fixtures/equipment.json",
        "features/fixtures/features.json",
    ]

    def test_character_class_list_pagination(self):
        url = "/api/character/class/list/"
        page_size = 2

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 4)
        self.assertEqual(len(response.data["results"]), response.data["count"])
        self.assertIsNone(response.data.get("previous"))
        self.assertIsNone(response.data.get("next"))
        expected_first_result = response.data["results"][0]
        next_expected_first_result = response.data["results"][page_size]

        response = self.client.post(f"{url}?page_size={page_size}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 4)
        self.assertIsNone(response.data.get("previous"))
        self.assertEqual(len(response.data["results"]), page_size)
        self.assertEqual(response.data["results"][0], expected_first_result)
        next_link = response.data["next"]

        response = self.client.post(f"{url}{next_link}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 4)
        self.assertIsNone(response.data.get("next"))
        self.assertEqual(len(response.data["results"]), page_size)
        self.assertEqual(response.data["results"][0], next_expected_first_result)
        previous_link = response.data["previous"]

        response = self.client.post(f"{url}{previous_link}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0], expected_first_result)
