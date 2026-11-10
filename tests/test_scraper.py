import unittest
from src.scraper import ReviewScraper

class TestReviewScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = ReviewScraper()

    def test_json_ld_extraction(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script type="application/ld+json">
            {
              "@context": "https://schema.org/",
              "@type": "Product",
              "name": "AcousticPro Wireless Earbuds",
              "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.6",
                "reviewCount": "128"
              },
              "review": [
                {
                  "@type": "Review",
                  "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "5"
                  },
                  "author": {
                    "@type": "Person",
                    "name": "John Doe"
                  },
                  "datePublished": "2026-01-15",
                  "headline": "Amazing sound quality!",
                  "reviewBody": "These earbuds sound phenomenal. Deep bass and clear treble."
                },
                {
                  "@type": "Review",
                  "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "1"
                  },
                  "author": {
                    "@type": "Person",
                    "name": "Sarah K."
                  },
                  "datePublished": "2026-03-20",
                  "headline": "Broke after 2 months",
                  "reviewBody": "Left earbud stopped charging after 2 months. Total waste of money."
                }
              ]
            }
            </script>
        </head>
        <body>
            <h1>AcousticPro Wireless Earbuds</h1>
        </body>
        </html>
        """
        product, reviews = self.scraper.parse_html(html, "https://shop.example.com/earbuds")
        self.assertEqual(product.title, "AcousticPro Wireless Earbuds")
        self.assertEqual(product.claimed_rating, 4.6)
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0].rating, 5.0)
        self.assertEqual(reviews[1].rating, 1.0)
        self.assertIn("stopped charging after 2 months", reviews[1].body)

    def test_amazon_dom_extraction(self):
        html = """
        <html>
        <body>
            <span id="productTitle">UltraBlend 9000 Kitchen Blender</span>
            <span data-hook="rating-out-of-text">4.7 out of 5 stars</span>
            <span id="acrCustomerReviewText">1,450 ratings</span>

            <div id="customerReviews">
                <div data-hook="review" id="R12345">
                    <span class="a-profile-name">TechGeek</span>
                    <i data-hook="review-star-rating"><span>5.0 out of 5 stars</span></i>
                    <a data-hook="review-title"><span>Best blender ever made!</span></a>
                    <span data-hook="review-date">Reviewed in the United States on January 10, 2026</span>
                    <span data-hook="avp-badge">Verified Purchase</span>
                    <span data-hook="review-body">Blends frozen fruit in seconds with no chunks left behind.</span>
                </div>
                <div data-hook="review" id="R67890">
                    <span class="a-profile-name">DisappointedBuyer</span>
                    <i data-hook="review-star-rating"><span>1.0 out of 5 stars</span></i>
                    <a data-hook="review-title"><span>Motor died after 3 months</span></a>
                    <span data-hook="review-date">Reviewed in the United States on April 5, 2026</span>
                    <span data-hook="review-body">Smelled smoke and motor died after 3 months of light smoothie making.</span>
                </div>
            </div>
        </body>
        </html>
        """
        product, reviews = self.scraper.parse_html(html, "https://www.amazon.com/dp/B0Blender9000")
        self.assertEqual(product.platform, "amazon")
        self.assertEqual(product.title, "UltraBlend 9000 Kitchen Blender")
        self.assertEqual(product.claimed_rating, 4.7)
        self.assertEqual(product.total_reviews_count, 1450)
        self.assertEqual(len(reviews), 2)
        self.assertTrue(reviews[0].verified_purchase)
        self.assertEqual(reviews[0].rating, 5.0)
        self.assertEqual(reviews[1].rating, 1.0)
        self.assertIn("Motor died after 3 months", reviews[1].title)

if __name__ == "__main__":
    unittest.main()
