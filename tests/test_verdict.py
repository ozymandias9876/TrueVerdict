import unittest

from src.engine import TrueVerdictEngine
from src.models import (
    AuthenticityReport,
    DurabilityReport,
    ProductInfo,
    RedditConsensus,
    Review,
)


def _organic_reviews(n=8):
    return [
        Review(id=str(i), rating=5.0 if i % 2 else 4.0, verified_purchase=True,
               body=f"Solid laptop, battery lasts all day and the display is sharp. Review number {i} with specifics.")
        for i in range(n)
    ]


class TestVerdictSynthesis(unittest.TestCase):
    def setUp(self):
        self.engine = TrueVerdictEngine()

    def test_unknown_product_on_reddit_is_not_do_not_buy(self):
        auth = AuthenticityReport(score=100, grade="A")
        durability = DurabilityReport(durability_score=100)
        reddit = RedditConsensus(found_discussions=False, sentiment="Do Not Buy", confidence="Low")

        verdict, color, reasons = self.engine._determine_final_verdict(auth, durability, reddit)

        self.assertEqual(verdict, "RECOMMENDED")
        self.assertEqual(reasons, [])

    def test_reliable_negative_reddit_still_blocks(self):
        auth = AuthenticityReport(score=100, grade="A")
        durability = DurabilityReport(durability_score=100)
        reddit = RedditConsensus(found_discussions=True, sentiment="Do Not Buy", confidence="High")

        verdict, _, reasons = self.engine._determine_final_verdict(auth, durability, reddit)

        self.assertEqual(verdict, "DO NOT BUY")
        self.assertIn("Reddit", reasons[0])

    def test_headline_names_actual_reason(self):
        product = ProductInfo(title="Generic Blender", claimed_rating=4.4)
        reviews = [
            Review(id="1", rating=1.0, body="Motor burned out after 2 months.", verified_purchase=True),
            Review(id="2", rating=1.0, body="Stopped working after 3 weeks, motor died.", verified_purchase=True),
            Review(id="3", rating=5.0, body="Makes smoothies fine.", verified_purchase=True),
        ]

        result = self.engine.evaluate_data(product, reviews)

        self.assertEqual(result.final_verdict, "DO NOT BUY")
        self.assertIn("durability", result.headline)
        self.assertNotIn("review manipulation", result.headline)

    def test_true_rating_never_exceeds_claimed(self):
        product = ProductInfo(title="Apple 2026 MacBook Neo 13", claimed_rating=4.7, total_reviews_count=441)

        result = self.engine.evaluate_data(product, _organic_reviews())

        self.assertLessEqual(result.adjusted_star_rating, 4.7)


if __name__ == "__main__":
    unittest.main()
