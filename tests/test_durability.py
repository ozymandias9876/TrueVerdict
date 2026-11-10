import unittest
from src.models import Review, ProductInfo
from src.durability_engine import DurabilityEngine


class TestDurabilityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DurabilityEngine()

    def test_two_month_failure_detection(self):
        product = ProductInfo(title="SonicPulse Wireless Headphones")
        reviews = [
            Review(id="1", rating=1.0, title="Broke after 2 months", body="Left earbud stopped charging after 2 months of normal use. Won't hold charge anymore."),
            Review(id="2", rating=1.0, title="Terrible battery life", body="After 3 months the battery died completely and won't turn on."),
            Review(id="3", rating=2.0, title="Plastic hinge cracked", body="The plastic hinge cracked after 6 weeks when taking them off my head."),
            Review(id="4", rating=5.0, title="Great sound", body="Love these! Crisp sound and comfy ear pads."),
        ]

        report = self.engine.analyze(reviews, product)
        
        # Verify timeline breakdown
        self.assertGreater(report.timeline_breakdown.get("1-3 months", 0), 0)
        
        # Verify components at risk
        comp_names = [c["component"] for c in report.components_at_risk]
        self.assertTrue(any("Battery" in c for c in comp_names))
        
        # Verify fatal flaws
        self.assertTrue(len(report.fatal_flaws) > 0)
        self.assertLess(report.durability_score, 80)

    def test_durable_product_clean_slate(self):
        product = ProductInfo(title="Cast Iron Skillet 12-inch")
        reviews = [
            Review(id="1", rating=5.0, body="Indestructible pan. Heats evenly and has great seasoning."),
            Review(id="2", rating=5.0, body="Been using it every single day for cooking steaks. Perfect."),
            Review(id="3", rating=4.0, body="A bit heavy to lift with one hand, but cooks beautifully."),
        ]

        report = self.engine.analyze(reviews, product)
        self.assertGreaterEqual(report.durability_score, 80)
        self.assertEqual(report.timeline_breakdown.get("1-3 months", 0), 0)


if __name__ == "__main__":
    unittest.main()
