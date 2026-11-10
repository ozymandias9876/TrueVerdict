import os
import unittest

os.environ["GEMINI_API_KEY"] = ""  # load_dotenv() won't override this, keeping the test offline

from fastapi.testclient import TestClient  # noqa: E402

from server import app  # noqa: E402


class TestServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_reports_rules_engine_without_key(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["engine"], "rules")

    def test_analyze_accepts_extension_payload(self):
        payload = {
            "product": {"title": "Generic Jacket", "claimedRating": 4.2, "totalReviews": 300, "platform": "amazon"},
            "reviews": [
                {"title": "Zip broke", "body": "Zipper broke after 2 months.", "rating": 2, "verified": True, "dateStr": "2026-03-01"},
                {"title": "Nice", "body": "Warm and comfortable.", "rating": 5, "verified": True},
            ],
        }
        resp = self.client.post("/analyze", json=payload)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["engine"], "rules")
        self.assertEqual(body["product"]["claimed_rating"], 4.2)
        self.assertEqual(body["authenticity"]["analyzed_reviews_count"], 2)
        self.assertEqual(body["durability"]["timeline_breakdown"]["1-3 months"], 1)
        self.assertIn(body["verdict_badge_color"], ["green", "yellow", "red"])

    def test_analyze_rejects_missing_title(self):
        resp = self.client.post("/analyze", json={"product": {}, "reviews": []})
        self.assertEqual(resp.status_code, 422)

    def test_cors_allows_extension_origin(self):
        resp = self.client.options(
            "/analyze",
            headers={"Origin": "chrome-extension://abc", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(resp.headers.get("access-control-allow-origin"), "chrome-extension://abc")


if __name__ == "__main__":
    unittest.main()
