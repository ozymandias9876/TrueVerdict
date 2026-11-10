import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from src.models import Review, DurabilityReport, TemporalFailurePoint, ProductInfo


class DurabilityEngine:
    """
    Extracts the '6-Month Reality' from reviews:
    - Detects temporal failure anchors ('broke after 2 months', 'in week 3', '90 days later')
    - Maps failure modes to hardware/functional components
    - Aggregates failure timeline and clusters fatal flaws
    """

    # Temporal patterns matching time of failure
    TEMPORAL_PATTERNS = [
        # "broke after 2 months", "died after 3 weeks", "failed after 90 days"
        r"(?:broke|died|stopped working|failed|quit working|malfunctioned|cracked|burned out|died)\s+(?:after|within|around|in)\s+(\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(months?|weeks?|days?|years?)",
        # "after 2 months it stopped", "in 3 weeks the motor died"
        r"(?:after|within|in)\s+(\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(months?|weeks?|days?|years?)[,\s]+.*?(?:broke|died|stopped|quit|failed|issue|problem|crack|snap|dead|useless)",
        # "update: 2 months later"
        r"(?:update|edit|months later|weeks later):\s*(\d+|a|one|two|three|four|five|six)?\s*(?:months?|weeks?)?.*?(?:broke|died|stopped|fail|no longer)",
        # "died right outside return window"
        r"(?:outside|past|after)\s+(?:the\s+)?(?:return\s+window|warranty|30\s*days)"
    ]

    # Component keyword ontology
    COMPONENT_KEYWORDS = {
        "Battery & Charging": [
            "battery", "charge", "charging", "charger", "cord", "cable", "port", "usb-c", "plug", "power", "dead battery", "won't charge", "holds no charge"
        ],
        "Motor & Mechanical": [
            "motor", "engine", "gear", "pump", "blade", "fan", "grinder", "spin", "mechanism", "burned out", "smoke"
        ],
        "Structural & Build": [
            "hinge", "swivel", "arm", "snap", "snapped", "crack", "cracked", "joint", "screw", "clip", "handle", "latch", "broken piece", "flimsy", "plastic"
        ],
        "Seams & Fabric": [
            "zipper", "seam", "stitching", "fabric", "ripped", "peeling", "sole", "strap", "fraying"
        ],
        "Connectivity & Audio": [
            "bluetooth", "disconnect", "left earbud", "right earbud", "pairing", "static", "buzz", "mic", "microphone", "sound dropped"
        ],
        "Thermal & Liquid": [
            "leak", "leaking", "seal", "overheat", "overheating", "melt", "water damage", "burn"
        ],
        "Software & Controls": [
            "firmware", "app", "button", "sensor", "touch", "frozen", "screen", "display", "unresponsive"
        ]
    }

    WORD_TO_NUM = {
        "a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12
    }

    def __init__(self, gemini_client=None):
        self.gemini_client = gemini_client
        self.regexes = [re.compile(p, re.IGNORECASE) for p in self.TEMPORAL_PATTERNS]

    def analyze(self, reviews: List[Review], product: ProductInfo) -> DurabilityReport:
        if not reviews:
            return DurabilityReport(
                durability_score=85,
                durability_verdict="Insufficient long-term data",
                timeline_breakdown={},
                fatal_flaws=[]
            )

        temporal_failures: List[TemporalFailurePoint] = []
        component_counter = Counter_safe = defaultdict(int)
        timeline_counter = {
            "0-30 days": 0,
            "1-3 months": 0,
            "3-6 months": 0,
            "6-12 months": 0,
            "1+ year": 0
        }

        # Filter to critical reviews (1-3 stars) or reviews containing update/broke markers
        critical_reviews = [
            r for r in reviews 
            if r.rating <= 3.5 or any(k in f"{r.title} {r.body}".lower() for k in ["update", "months later", "broke", "stopped"])
        ]

        for r in critical_reviews:
            full_text = f"{r.title}. {r.body}"
            
            # 1. Search for temporal matches
            timeframe = self._extract_timeframe(full_text)
            
            # 2. Search for component failures
            component = self._detect_component(full_text)

            if timeframe or (component and r.rating <= 2.0):
                tf = timeframe or "1-3 months"  # default to typical post-purchase failure zone if unspecified
                timeline_counter[tf] += 1

                comp = component or "General Hardware"
                component_counter[comp] += 1

                # Extract the most relevant failure sentence as quote
                quote_sentence = self._extract_failure_sentence(full_text)

                temporal_failures.append(TemporalFailurePoint(
                    timeframe=tf,
                    component=comp,
                    failure_description=f"{comp} failure reported after {tf}",
                    quote=quote_sentence[:180],
                    review_rating=r.rating
                ))

        # Top components at risk
        components_at_risk = [
            {"component": comp, "mentions": count, "risk": "High" if count >= 3 else "Moderate"}
            for comp, count in sorted(component_counter.items(), key=lambda x: x[1], reverse=True)
            if count > 0
        ]

        # Calculate durability score
        # Considers both raw early failure counts and early failure percentage
        early_failure_count = timeline_counter["0-30 days"] + timeline_counter["1-3 months"]
        early_ratio = early_failure_count / len(reviews) if reviews else 0.0

        early_penalty = (timeline_counter["0-30 days"] * 10) + (timeline_counter["1-3 months"] * 15) + (timeline_counter["3-6 months"] * 5)
        # Ratio multiplier: if > 25% of reviews report early death, impose high penalty
        if early_ratio >= 0.30:
            early_penalty += int(early_ratio * 50)
        elif early_ratio >= 0.15:
            early_penalty += 20

        durability_score = max(15, min(100, 100 - early_penalty))

        # Durability verdict
        if durability_score >= 80:
            verdict = "Solid Durability (Low Failure Rate)"
        elif durability_score >= 60:
            verdict = "Moderate Durability (Monitor Key Components)"
        elif durability_score >= 40:
            verdict = "High Risk of Failure Within 90 Days"
        else:
            verdict = "Severe Durability Alert (Frequent Premature Breakdown)"

        # Extract Fatal Flaws
        fatal_flaws = self._summarize_fatal_flaws(temporal_failures, component_counter, product)

        return DurabilityReport(
            durability_score=durability_score,
            durability_verdict=verdict,
            timeline_breakdown=dict(timeline_counter),
            fatal_flaws=fatal_flaws,
            components_at_risk=components_at_risk,
            temporal_failures=temporal_failures,
            short_term_bias_warning=len(critical_reviews) < 2 and len(reviews) > 10
        )

    def _extract_timeframe(self, text: str) -> Optional[str]:
        """Maps temporal text to canonical buckets."""
        text_lower = text.lower()
        if "return window" in text_lower or "30 days" in text_lower or "week 2" in text_lower or "first week" in text_lower:
            return "0-30 days"

        for pattern in self.regexes:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    qty_str = groups[0] or "1"
                    unit = (groups[1] or "").lower()
                    
                    # Convert word number to int
                    qty = self.WORD_TO_NUM.get(qty_str.lower(), None)
                    if qty is None:
                        try:
                            qty = int(qty_str)
                        except ValueError:
                            qty = 1

                    if "day" in unit:
                        return "0-30 days" if qty <= 30 else "1-3 months"
                    elif "week" in unit:
                        return "0-30 days" if qty <= 4 else "1-3 months"
                    elif "month" in unit:
                        if qty <= 1:
                            return "0-30 days"
                        elif qty <= 3:
                            return "1-3 months"
                        elif qty <= 6:
                            return "3-6 months"
                        else:
                            return "6-12 months"
                    elif "year" in unit:
                        return "1+ year"

        # Explicit fallback keyword scanning
        if "2 months" in text_lower or "two months" in text_lower or "60 days" in text_lower:
            return "1-3 months"
        if "3 months" in text_lower or "three months" in text_lower or "90 days" in text_lower:
            return "1-3 months"
        if "6 months" in text_lower or "six months" in text_lower:
            return "3-6 months"
        if "1 year" in text_lower or "one year" in text_lower:
            return "1+ year"

        return None

    def _detect_component(self, text: str) -> Optional[str]:
        """Detects which component failed using word-boundary matching."""
        text_lower = text.lower()
        for comp_name, keywords in self.COMPONENT_KEYWORDS.items():
            for k in keywords:
                # Use regex with word boundaries to avoid false positives like 'port' in 'airport'
                pattern = r"\b" + re.escape(k) + r"\b"
                if re.search(pattern, text_lower):
                    return comp_name
        return None

    def _extract_failure_sentence(self, text: str) -> str:
        """Finds the most descriptive failure sentence."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        failure_triggers = ["broke", "died", "stop", "fail", "quit", "crack", "burn", "leak", "dead", "issue"]
        for s in sentences:
            if any(t in s.lower() for t in failure_triggers):
                return s.strip()
        return sentences[0].strip() if sentences else text[:120]

    def _summarize_fatal_flaws(self, failures: List[TemporalFailurePoint], component_counter: Dict[str, int], product: ProductInfo) -> List[str]:
        """Synthesizes top fatal flaws."""
        flaws = []
        # If we have Gemini available, we can ask for a synthesized 3-bullet summary
        if self.gemini_client and failures:
            try:
                sample_quotes = "\n".join([f"- ({f.timeframe}, {f.component}): \"{f.quote}\"" for f in failures[:8]])
                prompt = (
                    f"Product: {product.title}\n"
                    f"Here are user failure reports after prolonged use:\n{sample_quotes}\n\n"
                    "Extract exactly 2 to 3 concise, highly-specific bullet points detailing when and how this product breaks or fails (e.g. 'Battery degradation: Loses charge within 60-90 days'). "
                    "Output ONLY the bullet points, no preamble."
                )
                response = self.gemini_client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt
                )
                if response and response.text:
                    lines = [line.strip().lstrip("-*• ") for line in response.text.strip().split("\n") if line.strip()]
                    if lines:
                        return lines[:3]
            except Exception:
                pass

        # Algorithmic rule-based fallback
        for comp, count in sorted(component_counter.items(), key=lambda x: x[1], reverse=True)[:3]:
            # find matching quotes
            matching = [f for f in failures if f.component == comp]
            timeframes = [m.timeframe for m in matching if m.timeframe]
            tf_str = timeframes[0] if timeframes else "2-3 months"
            flaws.append(f"{comp}: {count} buyers report breakdown after {tf_str} ('{matching[0].quote[:80]}...')")

        if not flaws:
            flaws = ["No recurring fatal flaws detected in available review corpus."]

        return flaws
