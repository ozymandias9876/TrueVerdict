from typing import List, Optional
from google import genai

from src.models import (
    Review,
    ProductInfo,
    AuthenticityReport,
    DurabilityReport,
    RedditConsensus,
    VerdictResult
)
from src.scraper import ReviewScraper
from src.authenticity_engine import AuthenticityEngine
from src.durability_engine import DurabilityEngine
from src.reddit_checker import RedditChecker


class TrueVerdictEngine:
    """Master orchestrator combining Authenticity, Durability ('6-Month Reality'), and Reddit Consensus."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_client = None
        if gemini_api_key:
            try:
                self.gemini_client = genai.Client(api_key=gemini_api_key)
            except Exception:
                pass

        self.scraper = ReviewScraper()
        self.auth_engine = AuthenticityEngine()
        self.durability_engine = DurabilityEngine(gemini_client=self.gemini_client)
        self.reddit_checker = RedditChecker(gemini_client=self.gemini_client)

    def evaluate_html(self, html_content: str, url: str = "") -> VerdictResult:
        """Parses HTML directly and synthesizes a full TrueVerdict."""
        product, reviews = self.scraper.parse_html(html_content, url)
        return self.evaluate_data(product, reviews)

    def evaluate_data(self, product: ProductInfo, reviews: List[Review]) -> VerdictResult:
        """Evaluates extracted reviews and product info."""
        # 1. Authenticity Report
        auth_report = self.auth_engine.analyze(reviews, product)

        # 2. Durability Report ("The 6-Month Reality")
        durability_report = self.durability_engine.analyze(reviews, product)

        # 3. Reddit Consensus
        reddit_consensus = self.reddit_checker.get_consensus(product)

        # 4. Synthesize Final Verdict
        final_verdict, badge_color, reasons = self._determine_final_verdict(auth_report, durability_report, reddit_consensus)

        # 5. Headline & Key Takeaways
        headline, takeaways = self._generate_verdict_narrative(product, auth_report, durability_report, reddit_consensus, final_verdict, reasons)

        fatal_warning = None
        if durability_report.fatal_flaws and len(durability_report.fatal_flaws) > 0:
            if "No recurring fatal flaws" not in durability_report.fatal_flaws[0]:
                fatal_warning = durability_report.fatal_flaws[0]

        return VerdictResult(
            product=product,
            authenticity=auth_report,
            durability=durability_report,
            reddit=reddit_consensus,
            final_verdict=final_verdict,
            verdict_badge_color=badge_color,
            adjusted_star_rating=auth_report.adjusted_rating,
            headline=headline,
            key_takeaways=takeaways,
            fatal_flaws_warning=fatal_warning
        )

    def _determine_final_verdict(
        self,
        auth: AuthenticityReport,
        durability: DurabilityReport,
        reddit: RedditConsensus
    ) -> tuple[str, str, List[str]]:
        """Calculates BUY / CAUTION / DO NOT BUY with color code and the reasons that triggered it."""
        # Reddit only counts when there is actual evidence; "no discussions found" is neutral
        reddit_reliable = reddit.found_discussions and reddit.confidence != "Low"
        reddit_negative = reddit_reliable and ("Avoid" in reddit.sentiment or "Do Not Buy" in reddit.sentiment)
        reddit_mixed = reddit_reliable and "Mixed" in reddit.sentiment

        severe = []
        if auth.grade in ["D", "F"]:
            severe.append(f"heavy review manipulation (Grade {auth.grade} authenticity)")
        if durability.durability_score < 45:
            severe.append(f"frequent early breakdowns ({durability.durability_score}/100 durability)")
        if reddit_negative:
            severe.append("owners on Reddit widely report serious problems")
        if severe:
            return "DO NOT BUY", "red", severe

        caution = []
        if auth.grade == "C":
            caution.append("some reviews look manipulated (Grade C authenticity)")
        if auth.unverified_ratio > 0.25:
            caution.append(f"{round(auth.unverified_ratio * 100)}% of sampled reviews are unverified")
        if durability.durability_score < 75:
            caution.append(f"recurring component wear ({durability.durability_score}/100 durability)")
        if reddit_mixed:
            caution.append("mixed long-term owner sentiment on Reddit")
        if caution:
            return "PROCEED WITH CAUTION", "yellow", caution

        return "RECOMMENDED", "green", []

    def _generate_verdict_narrative(
        self,
        product: ProductInfo,
        auth: AuthenticityReport,
        durability: DurabilityReport,
        reddit: RedditConsensus,
        verdict: str,
        reasons: List[str]
    ) -> tuple[str, List[str]]:
        takeaways = []

        # Authenticity takeaway
        if auth.grade in ["A", "B"]:
            takeaways.append(f"Authentic Reviews: Grade {auth.grade} ({auth.score}% honest score). Little to no evidence of bot manipulation.")
        else:
            takeaways.append(f"Review Manipulation Warning: Grade {auth.grade} ({auth.score}% score). Rating artificially inflated from ~{auth.adjusted_rating} to {product.claimed_rating}.")

        # Durability takeaway
        if durability.timeline_breakdown.get("1-3 months", 0) > 0 or durability.timeline_breakdown.get("0-30 days", 0) > 0:
            takeaways.append(f"The 2-Month Reality: {durability.durability_verdict}. Critical failure reports clustered between 30 and 90 days.")
        else:
            takeaways.append(f"Longevity: {durability.durability_verdict}. Minimal early breakdown reports.")

        # Reddit takeaway
        if reddit.consensus_summary:
            takeaways.append(f"Reddit Consensus: {reddit.consensus_summary}")

        reason_text = "; ".join(reasons)
        if verdict == "DO NOT BUY":
            headline = f"Buyer Beware: {reason_text[:1].upper()}{reason_text[1:]}."
        elif verdict == "PROCEED WITH CAUTION":
            headline = f"Proceed with Caution: {reason_text[:1].upper()}{reason_text[1:]}."
        else:
            headline = f"Looks Legitimate: Grade {auth.grade} authenticity and {durability.durability_score}/100 durability in the sampled reviews."

        return headline, takeaways
