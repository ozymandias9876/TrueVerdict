import unittest
from src.engine import TrueVerdictEngine
from src.models import Review, ProductInfo

class TestTrueVerdictEngine(unittest.TestCase):
    def setUp(self):
        # Initialized without API key to test offline deterministic logic first
        self.engine = TrueVerdictEngine()

    def test_end_to_end_synthesis_scam_product(self):
        product = ProductInfo(
            title="FastCharge 100W Magnetic Power Bank",
            claimed_rating=4.9,
            total_reviews_count=200,
            platform="amazon"
        )
        # Reviews with AI markers, unverified 5-stars, and 2-month battery death
        reviews = [
            Review(id="1", rating=5.0, body="In conclusion, this product exceeded all expectations! A game changer in every sense.", verified_purchase=False, date_str="2026-03-01"),
            Review(id="2", rating=5.0, body="Cannot recommend enough! Five stars is not enough.", verified_purchase=False, date_str="2026-03-01"),
            Review(id="3", rating=5.0, body="Great product", verified_purchase=False, date_str="2026-03-01"),
            Review(id="4", rating=1.0, title="Died after 2 months", body="Battery stopped charging after 2 months. Won't turn on or charge my phone at all.", verified_purchase=True, date_str="2026-04-10"),
            Review(id="5", rating=1.0, title="Broke after 60 days", body="USB-C port cracked and stopped working after 2 months.", verified_purchase=True, date_str="2026-04-15"),
        ]

        result = self.engine.evaluate_data(product, reviews)

        self.assertEqual(result.final_verdict, "DO NOT BUY")
        self.assertEqual(result.verdict_badge_color, "red")
        self.assertLess(result.authenticity.score, 65)
        self.assertLess(result.durability.durability_score, 70)
        self.assertGreater(result.durability.timeline_breakdown.get("1-3 months", 0), 0)
        self.assertTrue(len(result.key_takeaways) >= 2)
        print("\n=== Test Synthesis Output ===")
        print(f"Product: {result.product.title}")
        print(f"Claimed Rating: {result.product.claimed_rating}★ -> Adjusted: {result.adjusted_star_rating}★")
        print(f"Verdict: {result.final_verdict} ({result.verdict_badge_color})")
        print(f"Authenticity Grade: {result.authenticity.grade} ({result.authenticity.score}%)")
        print(f"Durability Score: {result.durability.durability_score}/100")
        print(f"Fatal Flaws: {result.durability.fatal_flaws}")
        print(f"Headline: {result.headline}")

    def test_end_to_end_synthesis_legit_product(self):
        product = ProductInfo(
            title="Stainless Steel Kitchen Chef Knife 8-inch",
            claimed_rating=4.5,
            total_reviews_count=850,
            platform="shopify"
        )
        reviews = [
            Review(id="1", rating=5.0, body="Solid balance, keeps an edge nicely after weeks of chopping vegetables.", verified_purchase=True),
            Review(id="2", rating=4.0, body="Handle is comfortable wood. Needs hand washing and immediate drying to prevent spotting.", verified_purchase=True),
            Review(id="3", rating=5.0, body="Great chef knife for everyday prep. Slices through tomatoes cleanly.", verified_purchase=True),
            Review(id="4", rating=4.0, body="A bit heavier than German knives, but excellent sharpness.", verified_purchase=True),
        ]

        result = self.engine.evaluate_data(product, reviews)
        self.assertIn(result.final_verdict, ["RECOMMENDED", "PROCEED WITH CAUTION"])
        self.assertGreaterEqual(result.authenticity.score, 80)
        self.assertGreaterEqual(result.durability.durability_score, 80)


if __name__ == "__main__":
    unittest.main()
