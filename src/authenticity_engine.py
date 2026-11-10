import re
import math
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from datetime import datetime
from src.models import Review, AuthenticityReport, ProductInfo


class AuthenticityEngine:
    """Evaluates reviews to calculate authenticity score, detect manipulation, and compute True Rating."""

    # Formulaic AI/PR review phrases
    AI_MARKERS = [
        r"\bin conclusion\b",
        r"\bgame changer\b",
        r"\bexceeded (?:all )?(?:my )?expectations\b",
        r"\btestament to\b",
        r"\bcannot recommend (?:this )?enough\b",
        r"\blook no further\b",
        r"\bseamlessly integrates\b",
        r"\bi was initially skeptical\b",
        r"\bworth every (?:single )?penny\b",
        r"\ba must-have in every\b",
        r"\bhands down the best\b",
        r"\bpleasant surprise\b",
        r"\bfive stars is not enough\b",
        r"\b10/10 would recommend\b",
        r"\btop-notch craftsmanship\b",
        r"\bdelivers on all fronts\b",
        r"\bkudos to the manufacturer\b",
    ]

    GENERIC_SUPERLATIVES = [
        r"^(?:great|awesome|excellent|perfect|good|love it|amazing|nice product|works well)[.!]?$",
        r"^(?:fast shipping|arrived on time|as described|thank you)[.!]?$",
        r"^(?:very good quality|best purchase ever|highly recommend this item)[.!]?$"
    ]

    def __init__(self):
        self.ai_regexes = [re.compile(p, re.IGNORECASE) for p in self.AI_MARKERS]
        self.generic_regexes = [re.compile(p, re.IGNORECASE) for p in self.GENERIC_SUPERLATIVES]

    def analyze(self, reviews: List[Review], product: ProductInfo) -> AuthenticityReport:
        if not reviews:
            return AuthenticityReport(
                score=100,
                grade="A",
                flagged_reasons=["Insufficient reviews to detect patterns."]
            )

        total_count = len(reviews)
        star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in reviews:
            rounded_star = max(1, min(5, round(r.rating)))
            star_counts[rounded_star] += 1

        # 1. Linguistic AI, Review Syndicate & Marketing Analysis
        ai_flagged_count = 0
        generic_praise_count = 0
        suspicious_reviews = []

        # Detect cross-review duplicate sentences (Review Farming Syndicate)
        shingle_map = defaultdict(set)
        for idx, r in enumerate(reviews):
            words = re.findall(r"\b[a-zA-Z]{3,}\b", f"{r.title} {r.body}".lower())
            for i in range(len(words) - 5):
                shingle = " ".join(words[i:i+6])
                shingle_map[shingle].add(idx)

        syndicate_hits = {phrase: idxs for phrase, idxs in shingle_map.items() if len(idxs) > 1}
        review_farming_detected = len(syndicate_hits) >= 2

        for idx, r in enumerate(reviews):
            text = f"{r.title} {r.body}".strip()
            is_suspicious = False

            # Check if this review participates in review farming
            if any(idx in idxs for idxs in syndicate_hits.values()):
                is_suspicious = True

            # Check AI formulaic patterns
            marker_hits = sum(1 for pattern in self.ai_regexes if pattern.search(text))
            if marker_hits >= 2 or (marker_hits >= 1 and len(text.split()) < 30):
                ai_flagged_count += 1
                is_suspicious = True

            # Check generic non-specific praise
            if any(pattern.match(text) for pattern in self.generic_regexes):
                generic_praise_count += 1
                is_suspicious = True

            # Check exact product title stuffing
            if product.title and len(product.title) > 15:
                # If exact long product title appears multiple times in body
                if text.lower().count(product.title.lower()) >= 2:
                    is_suspicious = True

            if is_suspicious:
                suspicious_reviews.append(r)

        ai_ratio = ai_flagged_count / total_count
        generic_ratio = generic_praise_count / total_count

        # 2. Verification & Incentivized Ratio
        unverified_count = sum(1 for r in reviews if not r.verified_purchase)
        incentivized_count = sum(1 for r in reviews if r.is_incentivized)
        
        # In particular, check unverified 5-star ratio
        unverified_5_stars = sum(1 for r in reviews if not r.verified_purchase and r.rating >= 4.5)
        total_5_stars = star_counts[5]

        unverified_ratio = unverified_count / total_count
        incentivized_ratio = incentivized_count / total_count

        # 3. Star Distribution Entropy & Bimodal J-Curve Check
        # Normal healthy distribution has a curve with 3 and 4 stars.
        # Suspicious fake profiles have 90%+ 5-stars, almost 0% 3/4 stars, and 10% 1-stars.
        middle_stars = star_counts[3] + star_counts[4]
        middle_ratio = middle_stars / total_count if total_count > 0 else 0.0

        j_curve_detected = False
        star_skew_penalty = 0
        if total_count >= 10:
            if star_counts[5] / total_count >= 0.85 and middle_ratio <= 0.05:
                j_curve_detected = True
                star_skew_penalty = 15

        # 4. Temporal Burst Check
        burst_detected, burst_msg = self._detect_temporal_burst(reviews)

        # 5. Calculate Authenticity Penalty
        penalty = 0
        flagged_reasons = []

        # Linguistic penalties
        if review_farming_detected:
            penalty += 45
            sample_phrase = list(syndicate_hits.keys())[0]
            flagged_reasons.append(f"Review Syndicate Detected: Multiple reviews share copy-pasted phrases ('...{sample_phrase}...').")

        if ai_ratio > 0.15:
            pen = min(30, int(ai_ratio * 70))
            penalty += pen
            flagged_reasons.append(f"{round(ai_ratio * 100)}% of reviews match formulaic AI or PR marketing patterns.")
        elif ai_ratio > 0.05:
            penalty += 10
            flagged_reasons.append("Slight elevation in robotic / template-driven phrasing.")

        if generic_ratio > 0.20:
            pen = min(20, int(generic_ratio * 40))
            penalty += pen
            flagged_reasons.append(f"{round(generic_ratio * 100)}% of reviews are generic 1-liner superlatives without specific details.")

        # Unverified / Incentivized penalties
        if total_5_stars > 0 and (unverified_5_stars / total_5_stars) > 0.40:
            penalty += 20
            flagged_reasons.append(f"{round((unverified_5_stars / total_5_stars) * 100)}% of 5-star ratings come from unverified purchases.")
        elif unverified_ratio > 0.35:
            penalty += 15
            flagged_reasons.append(f"High overall unverified purchase rate ({round(unverified_ratio * 100)}%).")

        if incentivized_ratio > 0.25:
            penalty += 15
            flagged_reasons.append(f"{round(incentivized_ratio * 100)}% of reviews are promotional or free product recipients (Vine / sponsored).")

        # J-curve distribution penalty
        if j_curve_detected:
            penalty += star_skew_penalty
            flagged_reasons.append("Unnatural rating distribution (severe J-curve): heavy 5-stars with near-zero 3 or 4-star nuance.")

        # Temporal burst penalty
        if burst_detected:
            penalty += 20
            flagged_reasons.append(f"Review velocity burst detected: {burst_msg}")

        # Final Authenticity Score & Grade
        final_score = max(5, min(100, 100 - penalty))
        grade = self._score_to_grade(final_score)

        # 6. Calculate True Adjusted Rating
        adjusted_rating = self._calculate_adjusted_rating(reviews, suspicious_reviews)

        return AuthenticityReport(
            score=final_score,
            grade=grade,
            ai_generated_ratio=round(ai_ratio, 2),
            unverified_ratio=round(unverified_ratio, 2),
            incentivized_ratio=round(incentivized_ratio, 2),
            burst_detected=burst_detected,
            burst_details=burst_msg if burst_detected else None,
            star_distribution=star_counts,
            flagged_reasons=flagged_reasons,
            adjusted_rating=round(adjusted_rating, 2),
            suspicious_reviews_count=len(suspicious_reviews),
            analyzed_reviews_count=total_count
        )

    def _score_to_grade(self, score: int) -> str:
        if score >= 90:
            return "A"
        if score >= 78:
            return "B"
        if score >= 65:
            return "C"
        if score >= 50:
            return "D"
        return "F"

    def _detect_temporal_burst(self, reviews: List[Review]) -> Tuple[bool, str]:
        """Checks if a disproportionate number of 5-star reviews were posted on the same date."""
        dates = [r.date_str for r in reviews if r.date_str and r.rating >= 4.5]
        if len(dates) < 5:
            return False, ""

        date_counter = Counter(dates)
        most_common_date, count = date_counter.most_common(1)[0]
        # If > 50% of 5-star reviews were published on one single date
        if count >= 4 and (count / len(dates)) >= 0.50:
            return True, f"{count} glowing 5-star reviews clustered on a single date ({most_common_date})."

        return False, ""

    def _calculate_adjusted_rating(self, all_reviews: List[Review], suspicious_reviews: List[Review]) -> float:
        """
        Re-weights reviews to strip out artificial inflation:
        - Suspicious reviews: 0.15 weight
        - Unverified 5-star reviews: 0.3 weight
        - Incentivized reviews: 0.5 weight
        - Verified, detailed organic reviews: 1.0 weight
        """
        suspicious_ids = {r.id for r in suspicious_reviews}
        weighted_sum = 0.0
        total_weight = 0.0

        for r in all_reviews:
            weight = 1.0

            if r.id in suspicious_ids:
                weight *= 0.20

            if not r.verified_purchase and r.rating >= 4.0:
                weight *= 0.35

            if r.is_incentivized:
                weight *= 0.50

            # Reward longer, detailed reviews (likely real human experience)
            word_count = len(r.body.split())
            if word_count > 40 and r.verified_purchase:
                weight *= 1.25

            weighted_sum += r.rating * weight
            total_weight += weight

        if total_weight == 0:
            return sum(r.rating for r in all_reviews) / len(all_reviews) if all_reviews else 5.0

        return weighted_sum / total_weight
