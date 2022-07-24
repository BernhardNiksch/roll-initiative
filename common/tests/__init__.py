from unittest.mock import patch

from django.test import SimpleTestCase

from ..helpers import ability_modifier, roll, roll_multiple_dice, result_values_for_field


class TestHelpers(SimpleTestCase):
    def test_ability_modifier(self):
        modifiers = ((1, -5), (2, -4), (3, -4), (4, -3), (15, 2), (16, 3), (17, 3), (18, 4))
        for score, expected_modifier in modifiers:
            self.assertEqual(ability_modifier(score), expected_modifier)

    @patch('random.randint')
    def test_roll(self, mock_randint):
        mock_randint.return_value = 4
        roll_results = roll(6)
        self.assertEqual(roll_results["rolled"], [4])
        self.assertEqual(roll_results["results"], [4])
        self.assertEqual(roll_results["total"], 4)

        mock_randint.side_effect = [4, 2, 3, 1]
        roll_results = roll(6, 4, modifier=2, drop_lowest=2)
        self.assertEqual(roll_results["rolled"], [4, 2, 3, 1])
        self.assertEqual(roll_results["results"], [3, 4])
        self.assertEqual(roll_results["modifier"], 2)
        self.assertEqual(roll_results["total"], 9)

        mock_randint.side_effect = [4, 5, 2, 1, 1]
        roll_results = roll(6, dice_count=5, modifier=3, drop_lowest=1, drop_highest=2)
        self.assertEqual(roll_results["rolled"], [4, 5, 2, 1, 1])
        self.assertEqual(roll_results["results"], [1, 2])
        self.assertEqual(roll_results["modifier"], 3)
        self.assertEqual(roll_results["total"], 6)

    @patch('random.randint')
    def test_roll_multiple(self, mock_randint):
        mock_randint.return_value = 8
        roll_results = roll_multiple_dice({"20": 1})
        self.assertEqual(roll_results["modifier"], 0)
        self.assertEqual(roll_results["results"], {"20": [8]})
        self.assertEqual(roll_results["total"], 8)

        mock_randint.side_effect = [3, 4, 7, 16]
        roll_results = roll_multiple_dice({"6": 2, "12": 1, "20": 1}, modifier=2)
        self.assertEqual(roll_results["modifier"], 2)
        self.assertEqual(roll_results["results"], {"6": [3, 4], "12": [7], "20": [16]})
        self.assertEqual(roll_results["total"], 32)

    def test_result_values_for_field(self):
        values_a = [1, 2, 3]
        values_b = ["a", "b", "c"]
        results = []
        for a, b in zip(values_a, values_b):
            result = {
                "normal_field": a,
                "related_model": {
                    "blah": None,
                    "related_field": b,
                    "asdf": 0,
                },
                "ignored_field": "",
            }
            results.append(result)
        self.assertEqual(result_values_for_field(results, "normal_field"), values_a)
        self.assertEqual(result_values_for_field(results, "related_model__related_field"), values_b)
