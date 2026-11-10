import unittest
from src.models import Review, ProductInfo
from src.authenticity_engine import AuthenticityEngine


class TestAuthenticityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AuthenticityEngine()

    def test_organic_honest_reviews(self):
        product = ProductInfo(title="Ergonomic Mechanical Keyboard", claimed_rating=4.2)
        reviews = [
            Review(id="1", rating=5.0, body="Used this for typing code for 3 weeks. The blue switches are clicky and tactile. Keycaps are PBT.", verified_purchase=True, date_str="2026-01-10"),
            Review(id="2", rating=4.0, body="Good keyboard overall. The RGB software is a bit clunky on Mac, but typing feel is great.", verified_purchase=True, date_str="2026-01-18"),
            Review(id="3", rating=3.0, body="Average build quality. The plastic chassis creaks slightly if you press hard.", verified_purchase=True, date_str="2026-02-02"),
            Review(id="4", rating=2.0, body="Key chatter on the spacebar started happening after a month.", verified_purchase=True, date_str="2026-02-15"),
            Review(id="5", rating=5.0, body="Very comfortable wrist rest, solid heavy base that stays in place on desk.", verified_purchase=True, date_str="2026-03-01"),
        ]

        report = self.engine.analyze(reviews, product)
        self.assertIn(report.grade, ["A", "B"])
        self.assertGreaterEqual(report.score, 80)
        self.assertFalse(report.burst_detected)
        self.assertEqual(report.unverified_ratio, 0.0)

    def test_fake_manipulated_reviews(self):
        product = ProductInfo(title="SuperSlim Miracle Charger", claimed_rating=5.0)
        reviews = [
            # Formulaic AI phrases & burst on 2026-04-01
            Review(id="1", rating=5.0, body="In conclusion, this product exceeded all expectations! A game changer in every sense of the word.", verified_purchase=False, date_str="2026-04-01"),
            Review(id="2", rating=5.0, body="I was initially skeptical, but look no further! Testament to craftsmanship.", verified_purchase=False, date_str="2026-04-01"),
            Review(id="3", rating=5.0, body="Five stars is not enough! Cannot recommend enough.", verified_purchase=False, date_str="2026-04-01"),
            Review(id="4", rating=5.0, body="Great product", verified_purchase=False, date_str="2026-04-01"),
            Review(id="5", rating=5.0, body="Awesome", verified_purchase=False, date_str="2026-04-01"),
            # Single angry real buyer
            Review(id="6", rating=1.0, body="This is completely fake. Stopped working on second day. Do not buy.", verified_purchase=True, date_str="2026-04-10"),
        ]

        report = self.engine.analyze(reviews, product)
        self.assertIn(report.grade, ["D", "F"])
        self.assertLess(report.score, 60)
        self.assertTrue(report.burst_detected)
        self.assertGreater(report.unverified_ratio, 0.5)
        self.assertLess(report.adjusted_rating, 3.5)  # significantly reduced from 5.0
        self.assertTrue(len(report.flagged_reasons) >= 2)


if __name__ == "__main__":
    unittest.main()
