"""
Smoke tests for ContentPlanner.

Run:  python3 -m pytest tests/ -v
  or: python3 -m unittest discover tests/
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.content_planner import ContentPlanner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _planner_no_config():
    """ContentPlanner with no config files (graceful degradation to defaults)."""
    return ContentPlanner(
        profile_path="nonexistent_profile.json",
        goals_path="nonexistent_goals.json",
        calendar_path="nonexistent_calendar.json",
    )


# ---------------------------------------------------------------------------
# generate_daily_plan
# ---------------------------------------------------------------------------

class TestGenerateDailyPlan(unittest.TestCase):

    def setUp(self):
        self.planner = _planner_no_config()

    def test_plan_has_required_keys(self):
        plan = self.planner.generate_daily_plan(day_of_week="tuesday")
        for key in ("date", "day_of_week", "theme", "is_thread_day", "recommendations",
                    "content_mix_compliance", "engagement_targets"):
            self.assertIn(key, plan, f"Missing key: {key}")

    def test_plan_has_at_least_two_recommendations(self):
        plan = self.planner.generate_daily_plan(day_of_week="monday")
        self.assertGreaterEqual(len(plan["recommendations"]), 2)

    def test_each_recommendation_has_required_fields(self):
        plan = self.planner.generate_daily_plan(day_of_week="wednesday")
        for rec in plan["recommendations"]:
            self.assertIn("pillar", rec)
            self.assertIn("pillar_label", rec)
            self.assertIn("reason", rec)
            self.assertIn("product_integration", rec)
            self.assertIn("multimodal_suggestion", rec)

    def test_pillar_values_are_valid(self):
        valid_pillars = {"value", "opinion", "story", "engagement"}
        plan = self.planner.generate_daily_plan(day_of_week="thursday")
        for rec in plan["recommendations"]:
            self.assertIn(rec["pillar"], valid_pillars)

    def test_product_integration_tier_is_1_or_2_by_default(self):
        plan = self.planner.generate_daily_plan(day_of_week="tuesday")
        for rec in plan["recommendations"]:
            tier_label = rec["product_integration"]["label"]
            self.assertIn(
                tier_label,
                {"Background Presence", "Contextual Reference"},
                "Default posts should not be Tier 3 Direct Promotion"
            )

    def test_thread_day_flagged_correctly(self):
        tuesday_plan = self.planner.generate_daily_plan(day_of_week="tuesday")
        monday_plan = self.planner.generate_daily_plan(day_of_week="monday")
        self.assertTrue(tuesday_plan["is_thread_day"])
        self.assertFalse(monday_plan["is_thread_day"])

    def test_thread_day_includes_note(self):
        plan = self.planner.generate_daily_plan(day_of_week="tuesday")
        self.assertIn("thread_note", plan)

    def test_trending_topics_included_when_provided(self):
        plan = self.planner.generate_daily_plan(
            day_of_week="monday",
            trending_topics=["AI Agents", "GPT-5"]
        )
        self.assertIn("trending_topics", plan)
        self.assertIn("trending_note", plan)

    def test_all_days_of_week_work(self):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            plan = self.planner.generate_daily_plan(day_of_week=day)
            self.assertIsNotNone(plan, f"Plan for {day} should not be None")
            self.assertGreater(len(plan["recommendations"]), 0)

    def test_day_auto_detected_when_not_provided(self):
        plan = self.planner.generate_daily_plan()
        self.assertIn(plan["day_of_week"],
                      ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])


# ---------------------------------------------------------------------------
# _check_mix_compliance
# ---------------------------------------------------------------------------

class TestCheckMixCompliance(unittest.TestCase):

    def setUp(self):
        self.planner = _planner_no_config()

    def test_empty_history_returns_compliance_structure(self):
        result = self.planner._check_mix_compliance({})
        self.assertIn("actual", result)
        self.assertIn("target", result)
        self.assertIn("deviations", result)
        self.assertIn("status", result)

    def test_on_track_when_perfectly_balanced(self):
        history = {"value": 4, "opinion": 2, "story": 2, "engagement": 2}
        result = self.planner._check_mix_compliance(history)
        self.assertIsNone(result["most_underrepresented"],
                          "No pillar should be flagged when reasonably balanced")

    def test_underrepresented_pillar_detected(self):
        # All story, nothing else
        history = {"value": 0, "opinion": 0, "story": 10, "engagement": 0}
        result = self.planner._check_mix_compliance(history)
        self.assertIsNotNone(result["most_underrepresented"])
        self.assertNotEqual(result["most_underrepresented"], "story")

    def test_needs_adjustment_status_when_imbalanced(self):
        history = {"value": 0, "opinion": 0, "story": 10, "engagement": 0}
        result = self.planner._check_mix_compliance(history)
        self.assertEqual(result["status"], "NEEDS_ADJUSTMENT")


# ---------------------------------------------------------------------------
# Content mix targets
# ---------------------------------------------------------------------------

class TestContentMixTargets(unittest.TestCase):

    def test_default_targets_sum_to_100(self):
        planner = _planner_no_config()
        total = sum(planner.content_mix_targets.values())
        self.assertEqual(total, 100)

    def test_default_targets_have_four_pillars(self):
        planner = _planner_no_config()
        self.assertEqual(set(planner.content_mix_targets.keys()),
                         {"value", "opinion", "story", "engagement"})


if __name__ == "__main__":
    unittest.main()
