import unittest

from calculator import CalculationError, calculate_blend, calculate_blend_actual


class BlendCalculatorTests(unittest.TestCase):
    def test_single_element_addition(self):
        result = calculate_blend(
            100.0, ["X"], {"X": 10.0}, {"X": 0.0},
            [{"name": "X master", "composition": {"X": 100.0}}],
        )
        self.assertAlmostEqual(result["master_alloys"][0]["kg"], 10.0)
        self.assertAlmostEqual(result["base_metal_kg"], 90.0)
        self.assertAlmostEqual(result["achieved_wt_pct"]["X"], 10.0)

    def test_two_element_additions(self):
        result = calculate_blend(
            100.0, ["X", "Y"],
            {"X": 10.0, "Y": 20.0},
            {"X": 0.0, "Y": 0.0},
            [
                {"name": "X master", "composition": {"X": 100.0, "Y": 0.0}},
                {"name": "Y master", "composition": {"X": 0.0, "Y": 100.0}},
            ],
        )
        self.assertAlmostEqual(result["master_alloys"][0]["kg"], 10.0)
        self.assertAlmostEqual(result["master_alloys"][1]["kg"], 20.0)
        self.assertAlmostEqual(result["base_metal_kg"], 70.0)

    def test_more_master_alloys_than_elements(self):
        result = calculate_blend(
            100.0, ["X"], {"X": 10.0}, {"X": 0.0},
            [
                {"name": "Pure X", "composition": {"X": 100.0}},
                {"name": "Dilute X", "composition": {"X": 50.0}},
            ],
        )
        self.assertAlmostEqual(result["master_alloys"][0]["kg"], 10.0)
        self.assertAlmostEqual(result["master_alloys"][1]["kg"], 0.0)

    def test_rejects_negative_addition(self):
        with self.assertRaises(CalculationError):
            calculate_blend(
                100.0, ["X"], {"X": 10.0}, {"X": 20.0},
                [{"name": "X master", "composition": {"X": 100.0}}],
            )

    def test_rejects_insufficient_master_alloys(self):
        with self.assertRaises(CalculationError):
            calculate_blend(
                100.0, ["X", "Y"], {"X": 1, "Y": 1}, {"X": 0, "Y": 0},
                [{"name": "one", "composition": {"X": 100, "Y": 0}}],
            )


class ActualBlendCalculatorTests(unittest.TestCase):
    def test_process_adjusted_single_element(self):
        result = calculate_blend_actual(
            100.0, ["Si"], {"Si": 7.0}, {"Si": 0.5},
            [{"name": "Al-50Si", "composition": {"Si": 50.0}}],
            95.0, {"Si": 90.0},
        )
        self.assertAlmostEqual(result["total_charge_kg"], 100.0 / 0.95)
        self.assertAlmostEqual(
            result["base_metal_kg"] + result["master_alloys"][0]["kg"],
            result["total_charge_kg"],
        )
        self.assertAlmostEqual(result["achieved_wt_pct"]["Si"], 7.0)

    def test_actual_mode_rejects_missing_recovery(self):
        with self.assertRaises(CalculationError):
            calculate_blend_actual(
                100.0, ["Si"], {"Si": 7.0}, {"Si": 0.5},
                [{"name": "Al-50Si", "composition": {"Si": 50.0}}],
                95.0, {"Si": 0.0},
            )


if __name__ == "__main__":
    unittest.main()
