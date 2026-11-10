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
        final_verdict, badge_color = self._determine_final_verdict(auth_report, durability_report, reddit_consensus)

        # 5. Headline & Key Takeaways
        headline, takeaways = self._generate_verdict_narrative(product, auth_report, durability_report, reddit_consensus, final_verdict)

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
    ) -> tuple[str, str]:
        """Calculates BUY / CAUTION / DO NOT BUY with color code."""
        # Fatal conditions for "DO NOT BUY"
        if auth.grade in ["D", "F"] or durability.durability_score < 45 or "Avoid" in reddit.sentiment or "Do Not Buy" in reddit.sentiment:
            return "DO NOT BUY", "red"

        # Caution conditions
        if auth.grade == "C" or durability.durability_score < 75 or "Mixed" in reddit.sentiment or auth.unverified_ratio > 0.25:
            return "PROCEED WITH CAUTION", "yellow"

        # Otherwise Recommended
        return "RECOMMENDED", "green"

    def _generate_verdict_narrative(
        self,
        product: ProductInfo,
        auth: AuthenticityReport,
        durability: DurabilityReport,
        reddit: RedditConsensus,
        verdict: str
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

        # Headline
        if verdict == "DO NOT BUY":
            headline = f"Buyer Beware: Heavy review distortion and elevated early breakdown risk ({auth.grade} Authenticity, {durability.durability_score}/100 Durability)."
        elif verdict == "PROCEED WITH CAUTION":
            headline = f"Mixed Reliability: Product functions initially, but watch for specific component wear ({auth.grade} Authenticity)."
        else:
            headline = f"Verified Legitimate: Genuine reviews confirm solid performance and trustworthy build quality."

        return headline, takeaways
