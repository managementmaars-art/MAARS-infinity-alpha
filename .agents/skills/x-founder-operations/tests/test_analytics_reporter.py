"""
Smoke tests for AnalyticsReporter.

Run:  python3 -m pytest tests/ -v
  or: python3 -m unittest discover tests/
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.analytics_reporter import AnalyticsReporter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _reporter():
    return AnalyticsReporter(goals_path="nonexistent_goals.json")


def _tweet(tweet_id, likes, retweets, replies, quotes, impressions,
           created_at="2026-01-01T12:00:00Z", text=None):
    return {
        "id": tweet_id,
        "text": text or f"tweet {tweet_id}",
        "createdAt": created_at,
        "metrics": {
            "likeCount": likes,
            "retweetCount": retweets,
            "replyCount": replies,
            "quoteCount": quotes,
            "impressionCount": impressions,
        },
    }


# ---------------------------------------------------------------------------
# generate_report
# ---------------------------------------------------------------------------

class TestGenerateReport(unittest.TestCase):

    def setUp(self):
        self.r = _reporter()

    def test_empty_list_returns_no_data_status(self):
        report = self.r.generate_report([])
        self.assertEqual(report["status"], "NO_DATA")

    def test_report_has_required_sections(self):
        tweets = [_tweet("t1", 10, 2, 1, 0, 500)]
        report = self.r.generate_report(tweets)
        for key in ("summary", "top_performers", "bottom_performers",
                    "benchmark_comparison", "recommendations", "timing_analysis"):
            self.assertIn(key, report, f"Missing section: {key}")

    def test_period_label_in_report(self):
        tweets = [_tweet("t1", 5, 1, 0, 0, 200)]
        report = self.r.generate_report(tweets, period_label="Week of 2026-01-01")
        self.assertEqual(report["period"], "Week of 2026-01-01")


# ---------------------------------------------------------------------------
# _compute_metrics
# ---------------------------------------------------------------------------

class TestComputeMetrics(unittest.TestCase):

    def setUp(self):
        self.r = _reporter()

    def test_single_tweet_correct_engagement_rate(self):
        tweets = [_tweet("t1", 10, 2, 1, 0, 500)]
        metrics = self.r._compute_metrics(tweets)
        # engagement = 10+2+1+0 = 13; rate = 13/500*100 = 2.6
        self.assertAlmostEqual(metrics["engagement_rate_pct"], 2.6, places=1)

    def test_multiple_tweets_avg_impressions(self):
        tweets = [
            _tweet("t1", 5, 0, 0, 0, 200),
            _tweet("t2", 10, 1, 1, 0, 800),
        ]
        metrics = self.r._compute_metrics(tweets)
        self.assertEqual(metrics["avg_impressions_per_tweet"], 500.0)

    def test_zero_impressions_returns_null_rate(self):
        tweets = [_tweet("t1", 0, 0, 0, 0, 0)]
        metrics = self.r._compute_metrics(tweets)
        self.assertIsNone(metrics["engagement_rate_pct"])

    def test_tweet_without_impressions_skipped(self):
        tweets = [
            _tweet("t1", 10, 0, 0, 0, 500),
            {"id": "t2", "metrics": {}},  # no impressionCount
        ]
        metrics = self.r._compute_metrics(tweets)
        self.assertEqual(metrics["tweets_with_complete_data"], 1)

    def test_engagement_breakdown_present(self):
        tweets = [_tweet("t1", 3, 1, 2, 0, 100)]
        metrics = self.r._compute_metrics(tweets)
        self.assertIn("engagement_breakdown", metrics)
        self.assertEqual(metrics["engagement_breakdown"]["likes"], 3)
        self.assertEqual(metrics["engagement_breakdown"]["replies"], 2)

    def test_reply_ratio_calculated(self):
        tweets = [_tweet("t1", 8, 2, 4, 2, 1000)]
        metrics = self.r._compute_metrics(tweets)
        # replies=4, total_engagement=16, ratio=25%
        self.assertAlmostEqual(metrics["engagement_quality"]["reply_ratio"], 25.0, places=0)


# ---------------------------------------------------------------------------
# _find_top_performers / _find_bottom_performers
# ---------------------------------------------------------------------------

class TestPerformerRanking(unittest.TestCase):

    def setUp(self):
        self.r = _reporter()
        self.tweets = [
            _tweet("t1", 10, 0, 0, 0, 100),   # ER 10%
            _tweet("t2",  1, 0, 0, 0, 100),   # ER  1%
            _tweet("t3",  5, 0, 0, 0, 100),   # ER  5%
            _tweet("t4",  2, 0, 0, 0, 100),   # ER  2%
        ]

    def test_top_performer_is_highest_er(self):
        tops = self.r._find_top_performers(self.tweets, n=1)
        self.assertEqual(tops[0]["id"], "t1")

    def test_bottom_performer_is_lowest_er(self):
        bottoms = self.r._find_bottom_performers(self.tweets, n=1)
        self.assertEqual(bottoms[0]["id"], "t2")

    def test_top_n_respected(self):
        tops = self.r._find_top_performers(self.tweets, n=2)
        self.assertEqual(len(tops), 2)

    def test_tweet_without_impressions_excluded_from_ranking(self):
        tweets = self.tweets + [{"id": "t5", "metrics": {}}]
        tops = self.r._find_top_performers(tweets, n=3)
        ids = [t["id"] for t in tops]
        self.assertNotIn("t5", ids)

    def test_top_performers_have_required_fields(self):
        tops = self.r._find_top_performers(self.tweets, n=2)
        for t in tops:
            for field in ("id", "impressions", "engagement_rate_pct", "likes", "replies"):
                self.assertIn(field, t, f"Missing field: {field}")


# ---------------------------------------------------------------------------
# _compare_benchmarks
# ---------------------------------------------------------------------------

class TestCompareBenchmarks(unittest.TestCase):

    def _reporter_with_stage(self, stage):
        r = AnalyticsReporter(goals_path="nonexistent.json")
        r.growth_stage = stage
        return r

    def test_exceptional_er_for_early_stage(self):
        r = self._reporter_with_stage("early")
        result = r._compare_benchmarks({"engagement_rate_pct": 15.0, "avg_impressions_per_tweet": 500})
        self.assertEqual(result["engagement_rate"]["rating"], "EXCEPTIONAL")

    def test_below_benchmark_er(self):
        r = self._reporter_with_stage("early")
        result = r._compare_benchmarks({"engagement_rate_pct": 0.5, "avg_impressions_per_tweet": 100})
        self.assertEqual(result["engagement_rate"]["rating"], "BELOW_BENCHMARK")

    def test_null_er_returns_na(self):
        r = self._reporter_with_stage("growth")
        result = r._compare_benchmarks({"engagement_rate_pct": None, "avg_impressions_per_tweet": None})
        self.assertEqual(result["engagement_rate"]["rating"], "N/A")

    def test_growth_stage_uses_stricter_benchmarks_than_early(self):
        r_early = self._reporter_with_stage("early")
        r_growth = self._reporter_with_stage("growth")
        # ER of 1.5%: below early threshold (needs 2.0 for "good") but above growth threshold (needs 1.0 for "good")
        early_result = r_early._compare_benchmarks({"engagement_rate_pct": 1.5, "avg_impressions_per_tweet": 100})
        growth_result = r_growth._compare_benchmarks({"engagement_rate_pct": 1.5, "avg_impressions_per_tweet": 100})
        self.assertEqual(early_result["engagement_rate"]["rating"], "BELOW_BENCHMARK")
        self.assertEqual(growth_result["engagement_rate"]["rating"], "GOOD")


# ---------------------------------------------------------------------------
# _compare_periods
# ---------------------------------------------------------------------------

class TestComparePeriods(unittest.TestCase):

    def setUp(self):
        self.r = _reporter()

    def test_positive_growth_reflected(self):
        current = {"total_impressions": 1200, "engagement_rate_pct": 2.5, "avg_impressions_per_tweet": 300}
        previous = {"total_impressions": 1000, "engagement_rate_pct": 2.0, "avg_impressions_per_tweet": 250}
        result = self.r._compare_periods(current, previous)
        self.assertGreater(result["impressions_change_pct"], 0)
        self.assertGreater(result["engagement_rate_change"], 0)

    def test_zero_previous_returns_none(self):
        current = {"total_impressions": 500, "engagement_rate_pct": 2.0, "avg_impressions_per_tweet": 100}
        previous = {"total_impressions": 0, "engagement_rate_pct": 0, "avg_impressions_per_tweet": 0}
        result = self.r._compare_periods(current, previous)
        self.assertIsNone(result["impressions_change_pct"])

    def test_decline_shows_negative_change(self):
        current = {"total_impressions": 800, "engagement_rate_pct": 1.5, "avg_impressions_per_tweet": 160}
        previous = {"total_impressions": 1000, "engagement_rate_pct": 2.0, "avg_impressions_per_tweet": 200}
        result = self.r._compare_periods(current, previous)
        self.assertLess(result["impressions_change_pct"], 0)
        self.assertLess(result["engagement_rate_change"], 0)


# ---------------------------------------------------------------------------
# _generate_recommendations
# ---------------------------------------------------------------------------

class TestGenerateRecommendations(unittest.TestCase):

    def setUp(self):
        self.r = _reporter()

    def test_low_er_triggers_recommendation(self):
        metrics = {"engagement_rate_pct": 0.3, "engagement_quality": {"reply_ratio": 15}}
        recs = self.r._generate_recommendations(metrics, [], [], {})
        self.assertGreater(len(recs), 0)
        combined = " ".join(recs).lower()
        self.assertIn("engagement", combined)

    def test_low_reply_ratio_triggers_recommendation(self):
        metrics = {"engagement_rate_pct": 2.5, "engagement_quality": {"reply_ratio": 5}}
        recs = self.r._generate_recommendations(metrics, [], [], {})
        combined = " ".join(recs).lower()
        self.assertIn("repl", combined)

    def test_top_performer_referenced_in_recommendation(self):
        metrics = {"engagement_rate_pct": 3.0, "engagement_quality": {"reply_ratio": 30}}
        top = [{"id": "t1", "engagement_rate_pct": 8.5, "text_preview": "great tweet"}]
        recs = self.r._generate_recommendations(metrics, top, [], {})
        combined = " ".join(recs)
        self.assertIn("8.5", combined)


if __name__ == "__main__":
    unittest.main()
