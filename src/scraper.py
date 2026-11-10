import json
import re
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from src.models import Review, ProductInfo


class ReviewScraper:
    """Universal Review Scraper supporting Schema.org JSON-LD, microdata, and site-specific DOMs."""

    def __init__(self):
        pass

    def parse_html(self, html_content: str, url: str = "") -> Tuple[ProductInfo, List[Review]]:
        """Parses HTML content and returns ProductInfo and a list of Review objects."""
        soup = BeautifulSoup(html_content, "html.parser")
        platform = self.detect_platform(url, html_content)

        product = ProductInfo(url=url, platform=platform)
        reviews: List[Review] = []

        # 1. First, attempt to extract via Schema.org JSON-LD (standard across modern e-commerce)
        json_ld_product, json_ld_reviews = self._extract_json_ld(soup, url)
        if json_ld_reviews:
            reviews.extend(json_ld_reviews)
            if json_ld_product.title:
                product = json_ld_product
                product.platform = platform

        # 2. If platform-specific DOM has richer metadata or more reviews, parse DOM
        dom_product, dom_reviews = self._extract_platform_dom(soup, platform, url)

        # Merge or prioritize DOM reviews if JSON-LD was absent or sparse
        if not reviews or len(dom_reviews) > len(reviews):
            reviews = dom_reviews
        
        # Merge product details
        if dom_product.title and not product.title:
            product.title = dom_product.title
        if dom_product.claimed_rating > 0 and product.claimed_rating == 0:
            product.claimed_rating = dom_product.claimed_rating
        if dom_product.total_reviews_count > 0 and product.total_reviews_count == 0:
            product.total_reviews_count = dom_product.total_reviews_count
        if dom_product.price and not product.price:
            product.price = dom_product.price

        # Fallback for product title and rating if still empty
        if not product.title:
            product.title = self._fallback_title(soup)
        if product.claimed_rating == 0 and reviews:
            product.claimed_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
        if product.total_reviews_count == 0:
            product.total_reviews_count = len(reviews)

        return product, reviews

    def detect_platform(self, url: str, html: str) -> str:
        """Determines the e-commerce platform."""
        url_lower = url.lower()
        if "amazon." in url_lower or "amzn." in url_lower:
            return "amazon"
        if "walmart." in url_lower:
            return "walmart"
        if "target." in url_lower:
            return "target"
        if "bestbuy." in url_lower:
            return "bestbuy"
        if "shopify" in html.lower() or "cdn.shopify.com" in html:
            return "shopify"
        return "generic"

    def _extract_json_ld(self, soup: BeautifulSoup, url: str) -> Tuple[ProductInfo, List[Review]]:
        """Extracts Schema.org JSON-LD product & review data."""
        product = ProductInfo(url=url)
        reviews: List[Review] = []

        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if not script.string:
                continue
            try:
                data = json.loads(script.string.strip())
            except Exception:
                continue

            # Can be a single object or list of objects
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue

                # Handle @graph wrapper
                graph_items = item.get("@graph", [item])
                for entry in graph_items:
                    entry_type = entry.get("@type", "")
                    if entry_type == "Product" or "Product" in entry_type:
                        product.title = entry.get("name", "")
                        if "aggregateRating" in entry and isinstance(entry["aggregateRating"], dict):
                            agg = entry["aggregateRating"]
                            try:
                                product.claimed_rating = float(agg.get("ratingValue", 0))
                                product.total_reviews_count = int(agg.get("reviewCount", 0))
                            except (ValueError, TypeError):
                                pass

                        # Extract reviews inside Product object
                        embedded_reviews = entry.get("review", [])
                        if isinstance(embedded_reviews, dict):
                            embedded_reviews = [embedded_reviews]
                        for r_item in embedded_reviews:
                            rev = self._normalize_json_ld_review(r_item)
                            if rev:
                                reviews.append(rev)

                    elif entry_type == "Review" or "Review" in entry_type:
                        rev = self._normalize_json_ld_review(entry)
                        if rev:
                            reviews.append(rev)

        return product, reviews

    def _normalize_json_ld_review(self, item: dict) -> Optional[Review]:
        """Converts Schema.org Review dict into Review model."""
        if not isinstance(item, dict):
            return None
        body = item.get("reviewBody", "") or item.get("description", "")
        if not body:
            return None

        title = item.get("headline", "") or item.get("name", "")
        rating = 5.0
        rating_obj = item.get("reviewRating", {})
        if isinstance(rating_obj, dict):
            try:
                rating = float(rating_obj.get("ratingValue", 5.0))
            except (ValueError, TypeError):
                pass
        elif isinstance(rating_obj, (int, float)):
            rating = float(rating_obj)

        author_name = "Anonymous"
        author_obj = item.get("author", {})
        if isinstance(author_obj, dict):
            author_name = author_obj.get("name", "Anonymous")
        elif isinstance(author_obj, str):
            author_name = author_obj

        date_published = item.get("datePublished", "")

        return Review(
            id=str(abs(hash(body[:60]))),
            title=title,
            body=body,
            rating=rating,
            date_str=date_published,
            author=author_name,
            verified_purchase=True,
            is_incentivized=False
        )

    def _extract_platform_dom(self, soup: BeautifulSoup, platform: str, url: str) -> Tuple[ProductInfo, List[Review]]:
        """Extracts reviews using targeted CSS selectors for major platforms."""
        product = ProductInfo(url=url, platform=platform)
        reviews: List[Review] = []

        if platform == "amazon":
            # Product Title: check hidden input first or span#productTitle
            title_node = soup.select_one("input[name='productTitle']")
            if title_node and title_node.get("value", "").strip():
                product.title = title_node.get("value", "").strip()
            else:
                title_node = soup.select_one("#productTitle, #title span, h1.product-title")
                if title_node:
                    product.title = title_node.get_text(strip=True)

            # Claimed Rating
            rating_node = soup.select_one("span[data-hook='rating-out-of-text'], span.a-icon-alt, #acrPopover span")
            if rating_node:
                match = re.search(r"(\d+(?:\.\d+)?)\s*(?:out of|von|\/)\s*5", rating_node.get_text())
                if match:
                    product.claimed_rating = float(match.group(1))

            # Total Reviews Count
            count_node = soup.select_one("#acrCustomerReviewText, [data-hook='total-review-count']")
            if count_node:
                count_digits = re.sub(r"[^\d]", "", count_node.get_text())
                if count_digits:
                    product.total_reviews_count = int(count_digits)

            # Review Cards
            review_cards = soup.select("div[data-hook='review'], div.review, [data-testid='review-card']")
            for card in review_cards:
                r_id = card.get("id", "")
                
                # Title
                r_title = ""
                r_title_node = card.select_one("[data-hook='reviewTitle'], [data-hook='review-title'], a.review-title, span.review-title, h5")
                if r_title_node:
                    r_title = r_title_node.get_text(strip=True)
                    # Amazon often prepends star rating in review title
                    r_title = re.sub(r"^\d+(?:\.\d+)?\s*(?:out of 5 stars|stars)\s*", "", r_title, flags=re.I).strip()

                # Body
                r_body = ""
                rich_node = card.select_one("[data-hook='reviewRichContentContainer']")
                if rich_node:
                    r_body = rich_node.get_text(strip=True)
                else:
                    r_body_node = card.select_one("[data-hook='reviewText'], [data-hook='review-body'], span.review-text-content, div.review-text")
                    if r_body_node:
                        # strip teaser text
                        for t in r_body_node.select(".a-teaser-describedby-collapsed, .a-teaser-describedby-expanded"):
                            t.decompose()
                        r_body = r_body_node.get_text(strip=True)

                if not r_body and not r_title:
                    continue

                # Rating
                r_rating = 5.0
                star_node = card.select_one("[data-hook='review-star-rating'], i.a-icon-star, span.a-icon-alt")
                if star_node:
                    s_match = re.search(r"(\d+(?:\.\d+)?)", star_node.get_text())
                    if s_match:
                        r_rating = float(s_match.group(1))

                # Date
                r_date = ""
                date_node = card.select_one("[data-hook='review-date'], span.review-date")
                if date_node:
                    r_date = date_node.get_text(strip=True)

                # Author
                r_author = "Amazon Customer"
                author_node = card.select_one("span.a-profile-name, .reviewer")
                if author_node:
                    r_author = author_node.get_text(strip=True)

                # Verified Purchase
                is_verified = bool(card.select_one("[data-hook='avp-badge'], span:-soup-contains('Verified Purchase')"))
                if not is_verified:
                    # check text search
                    if "verified purchase" in card.get_text().lower():
                        is_verified = True

                # Incentivized / Vine
                is_incentivized = False
                card_text_lower = card.get_text().lower()
                if "vine customer review of free product" in card_text_lower or "free product" in card_text_lower:
                    is_incentivized = True

                # Helpful votes
                helpful_votes = 0
                helpful_node = card.select_one("[data-hook='helpful-vote-statement']")
                if helpful_node:
                    h_match = re.search(r"(\d+)", helpful_node.get_text())
                    if h_match:
                        helpful_votes = int(h_match.group(1))

                reviews.append(Review(
                    id=r_id or str(abs(hash(r_body[:60]))),
                    title=r_title,
                    body=r_body,
                    rating=r_rating,
                    date_str=r_date,
                    author=r_author,
                    verified_purchase=is_verified,
                    is_incentivized=is_incentivized,
                    helpful_votes=helpful_votes
                ))

        elif platform == "walmart":
            # Walmart title & reviews
            title_node = soup.select_one("h1[itemprop='name'], h1.prod-ProductTitle, #main-title")
            if title_node:
                product.title = title_node.get_text(strip=True)

            cards = soup.select("[data-automation-id='review-item'], div.review-item, div.customer-review")
            for card in cards:
                body_node = card.select_one(".review-text, [itemprop='reviewBody'], span.tl-m")
                body = body_node.get_text(strip=True) if body_node else ""
                title_node = card.select_one(".review-title, h3, [itemprop='name']")
                title = title_node.get_text(strip=True) if title_node else ""
                if not body:
                    continue

                rating = 5.0
                rating_node = card.select_one(".review-star, span.w_iUH7, [itemprop='ratingValue']")
                if rating_node:
                    r_m = re.search(r"(\d+(?:\.\d+)?)", rating_node.get_text())
                    if r_m:
                        rating = float(r_m.group(1))

                is_verified = "verified" in card.get_text().lower()
                is_incentivized = "incentivized" in card.get_text().lower() or "received free" in card.get_text().lower()

                reviews.append(Review(
                    id=str(abs(hash(body[:60]))),
                    title=title,
                    body=body,
                    rating=rating,
                    author="Walmart Shopper",
                    verified_purchase=is_verified,
                    is_incentivized=is_incentivized
                ))

        else:
            # Generic DOM parser: search for semantic review elements
            generic_cards = soup.select("[itemprop='review'], .review-item, .customer-review, .user-review, article.review")
            for card in generic_cards:
                body_node = card.select_one("[itemprop='reviewBody'], .review-body, .comment-content, p")
                body = body_node.get_text(strip=True) if body_node else ""
                if not body or len(body) < 10:
                    continue
                title_node = card.select_one("[itemprop='name'], h3, h4, .review-title")
                title = title_node.get_text(strip=True) if title_node else ""
                reviews.append(Review(
                    id=str(abs(hash(body[:60]))),
                    title=title,
                    body=body,
                    rating=5.0,
                    author="Customer",
                    verified_purchase=True
                ))

        return product, reviews

    def _fallback_title(self, soup: BeautifulSoup) -> str:
        """Finds the most probable product title from the page."""
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            clean_title = re.sub(r"\s*[-|:].*$", "", title_tag.get_text(strip=True))
            return clean_title
        return "Unknown Product"
