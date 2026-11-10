from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class Review(BaseModel):
    """Normalized review object parsed from any e-commerce platform."""
    id: str = ""
    title: str = ""
    body: str = ""
    rating: float = 5.0
    date_str: str = ""
    author: str = ""
    verified_purchase: bool = True
    helpful_votes: int = 0
    is_incentivized: bool = False  # e.g., Vine, promotion, free sample
    raw_html: Optional[str] = None


class ProductInfo(BaseModel):
    """Normalized product metadata."""
    title: str = ""
    url: str = ""
    platform: str = "generic"  # amazon, walmart, target, shopify, bestbuy, generic
    claimed_rating: float = 0.0
    total_reviews_count: int = 0
    price: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None


class AuthenticityReport(BaseModel):
    """Output from the Fake Review Detection Engine."""
    score: int = 100  # 0 to 100
    grade: str = "A"  # A, B, C, D, F
    ai_generated_ratio: float = 0.0
    unverified_ratio: float = 0.0
    incentivized_ratio: float = 0.0
    burst_detected: bool = False
    burst_details: Optional[str] = None
    star_distribution: Dict[int, int] = Field(default_factory=dict)
    flagged_reasons: List[str] = Field(default_factory=list)
    adjusted_rating: float = 5.0
    suspicious_reviews_count: int = 0
    analyzed_reviews_count: int = 0


class TemporalFailurePoint(BaseModel):
    """Specific failure incident tied to a temporal milestone."""
    timeframe: str  # "0-30 days", "1-3 months", "3-6 months", "6-12 months", "1+ year"
    component: str  # "Battery", "Hinge", "Motor", "Zipper", "Heating Element", "Audio/Bluetooth", etc.
    failure_description: str
    quote: str
    review_rating: float = 1.0


class DurabilityReport(BaseModel):
    """Output from the Durability & Flaw Extractor ('The 6-Month Reality')."""
    durability_score: int = 80  # 0 to 100 (100 = Built to Last)
    durability_verdict: str = "Acceptable Durability"
    timeline_breakdown: Dict[str, int] = Field(default_factory=dict)  # e.g. {"1-3 months": 8, "3-6 months": 4}
    fatal_flaws: List[str] = Field(default_factory=list)  # Top recurring dealbreakers
    components_at_risk: List[Dict[str, Any]] = Field(default_factory=list)  # e.g. [{"name": "Battery", "failures": 6}]
    temporal_failures: List[TemporalFailurePoint] = Field(default_factory=list)
    short_term_bias_warning: bool = False  # True if 90%+ reviews are written within first 7 days


class RedditQuote(BaseModel):
    quote: str
    subreddit: str
    score: int = 0
    url: str = ""


class RedditConsensus(BaseModel):
    """Output from the Reddit Organic Community Validator."""
    found_discussions: bool = False
    sentiment: str = "Neutral / Insufficient Data"  # "Strongly Recommended", "Mixed", "Avoid", etc.
    confidence: str = "Low"  # High, Moderate, Low
    subreddits_checked: List[str] = Field(default_factory=list)
    consensus_summary: str = ""
    top_quotes: List[RedditQuote] = Field(default_factory=list)


class VerdictResult(BaseModel):
    """Final synthesized TrueVerdict for the consumer."""
    product: ProductInfo
    authenticity: AuthenticityReport
    durability: DurabilityReport
    reddit: RedditConsensus
    final_verdict: str  # "RECOMMENDED", "PROCEED WITH CAUTION", "DO NOT BUY"
    verdict_badge_color: str  # "green", "yellow", "red"
    adjusted_star_rating: float
    headline: str
    key_takeaways: List[str] = Field(default_factory=list)
    fatal_flaws_warning: Optional[str] = None
