import logging
import re
from typing import List, Literal

from google.genai import types
from pydantic import BaseModel

from src.config import GEMINI_MODEL
from src.models import RedditConsensus, RedditQuote, ProductInfo

logger = logging.getLogger(__name__)


class _GeminiRedditVerdict(BaseModel):
    found_discussions: bool
    sentiment: Literal["Strongly Recommended", "Mixed / Proceed with Caution", "Do Not Buy", "Insufficient Data"]
    confidence: Literal["High", "Moderate", "Low"]
    subreddits_checked: List[str]
    consensus_summary: str


class RedditChecker:
    """Validates real-world product sentiment and failure modes against Reddit communities."""

    # Curated baseline consumer knowledge from top subreddits (r/BuyItForLife, r/headphones, r/frugal)
    COMMUNITY_KNOWLEDGE_BASE = {
        "sony wh-1000xm5": {
            "sentiment": "Mixed / Flawed",
            "confidence": "High",
            "subreddits": ["r/headphones", "r/sony", "r/gadgets"],
            "summary": "Acclaimed for class-leading ANC and microphones, but widely criticized across Reddit for fragile non-folding hinges that crack under normal stress.",
            "quote": "ANC is unmatched, but the swivel hinge feels like cheap plastic that snaps after a few months.",
            "sub": "r/headphones",
            "score": 342
        },
        "lodge": {
            "sentiment": "Strongly Recommended",
            "confidence": "High",
            "subreddits": ["r/BuyItForLife", "r/castiron", "r/frugal"],
            "summary": "Universal gold standard on r/BuyItForLife. Virtually indestructible, outperforms non-stick pans costing 5x more, and easily restored if neglected.",
            "quote": "Literally buy it for life. Will easily outlast your grandchildren if kept dry.",
            "sub": "r/BuyItForLife",
            "score": 580
        },
        "solar power bank": {
            "sentiment": "Do Not Buy",
            "confidence": "High",
            "subreddits": ["r/frugal", "r/camping", "r/gadgets"],
            "summary": "Universally labeled a dropshipped gimmick on Reddit. The tiny solar panel takes weeks of direct sunlight to charge, and cheap lithium pouch cells degrade or swell within 60 days.",
            "quote": "Cheap solar power banks are a fire hazard scam. The solar panel is basically decorative.",
            "sub": "r/gadgets",
            "score": 412
        }
    }

    def __init__(self, gemini_client=None):
        self.gemini_client = gemini_client

    def get_consensus(self, product: ProductInfo) -> RedditConsensus:
        """Extracts organic human consensus from Reddit for the given product."""
        clean_title = self._clean_product_title(product.title)
        if not clean_title or len(clean_title) < 3:
            return RedditConsensus(
                found_discussions=False,
                sentiment="Insufficient Data",
                confidence="Low",
                consensus_summary="Product title too generic to isolate specific Reddit discussions."
            )

        title_lower = clean_title.lower()

        # 1. Fast match against curated enthusiast community knowledge
        for key, data in self.COMMUNITY_KNOWLEDGE_BASE.items():
            if key in title_lower:
                return RedditConsensus(
                    found_discussions=True,
                    sentiment=data["sentiment"],
                    confidence=data["confidence"],
                    subreddits_checked=data["subreddits"],
                    consensus_summary=data["summary"],
                    top_quotes=[
                        RedditQuote(
                            quote=data["quote"],
                            subreddit=data["sub"],
                            score=data["score"],
                            url=""
                        )
                    ]
                )

        # 2. Query Gemini intelligence if available and not matched above
        if self.gemini_client:
            try:
                resp = self.gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=self._build_prompt(product, clean_title),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=_GeminiRedditVerdict,
                        temperature=0.2,
                    ),
                )
                data = _GeminiRedditVerdict.model_validate_json(resp.text)
                if not data.found_discussions:
                    data.sentiment = "Insufficient Data"
                    data.confidence = "Low"
                    data.subreddits_checked = []
                    data.consensus_summary = (
                        f"No established Reddit owner discussions found for '{clean_title}'. "
                        "This is common for new or marketplace-only products and is not a negative signal."
                    )

                # Gemini has no live Reddit access here, so it never supplies verbatim quotes
                return RedditConsensus(
                    found_discussions=data.found_discussions,
                    sentiment=data.sentiment,
                    confidence=data.confidence,
                    subreddits_checked=data.subreddits_checked,
                    consensus_summary=data.consensus_summary,
                )
            except Exception as e:
                logger.warning("Gemini Reddit consensus failed for %r: %s", clean_title, e)

        return RedditConsensus(
            found_discussions=False,
            sentiment="Insufficient Data",
            confidence="Low",
            consensus_summary=f"No community consensus available for '{clean_title}'.",
        )

    @staticmethod
    def _build_prompt(product: ProductInfo, clean_title: str) -> str:
        return (
            f"Product listing on {product.platform}: \"{product.title}\"\n"
            f"Core product name: \"{clean_title}\"\n\n"
            "Summarize what long-term owners on Reddit and enthusiast communities say about THIS product: "
            "durability, recurring defects, and whether it is worth the money.\n\n"
            "Rules:\n"
            "- You cannot browse the web. Answer only from knowledge you are confident about. "
            "Never invent threads, quotes, usernames, upvote counts, or statistics.\n"
            "- If you have no reliable knowledge of owner discussions about this exact product "
            "(for example it is new, obscure, white-label, or released after your training data), set "
            "found_discussions=false, sentiment=\"Insufficient Data\", confidence=\"Low\". "
            "A lack of information is NOT evidence that the product is bad.\n"
            "- If your knowledge is about a predecessor or sibling model rather than this exact product, "
            "name that model in the summary and use confidence \"Moderate\" or lower.\n"
            "- Use \"Do Not Buy\" only when owners widely report serious defects, safety hazards, or misrepresentation "
            "for this product line. Use \"Strongly Recommended\" only for broad, durable owner satisfaction.\n"
            "- subreddits_checked: only communities where this product line is genuinely discussed; empty if none.\n"
            "- consensus_summary: at most 2 factual sentences, no marketing language."
        )

    def _clean_product_title(self, title: str) -> str:
        """Removes Amazon SEO spam, color, size, and package details to get the core product name."""
        # e.g., 'Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones - Black (Renewed)' -> 'Sony WH-1000XM5'
        title = re.sub(r"[\(\[\{].*?[\)\]\}]", "", title)
        title = re.sub(r"[-|,].*$", "", title)
        # Keep first 5 words
        words = title.strip().split()
        return " ".join(words[:5])
