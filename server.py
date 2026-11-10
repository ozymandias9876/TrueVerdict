import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from src.config import GEMINI_MODEL  # noqa: E402  (reads GEMINI_MODEL from .env)
from src.engine import TrueVerdictEngine  # noqa: E402
from src.models import ProductInfo, Review, VerdictResult  # noqa: E402


class ExtensionProduct(BaseModel):
    """Product shape produced by extractPageData() in the extension."""
    title: str
    brand: str = ""
    claimedRating: float = 0.0
    totalReviews: int = 0
    platform: str = "generic"
    url: str = ""


class ExtensionReview(BaseModel):
    title: str = ""
    body: str = ""
    rating: float = 5.0
    author: str = ""
    dateStr: str = ""
    verified: bool = True
    incentivized: bool = False


class AnalyzeRequest(BaseModel):
    product: ExtensionProduct
    reviews: List[ExtensionReview] = []


class AnalyzeResponse(VerdictResult):
    engine: str


engine = TrueVerdictEngine(gemini_api_key=os.environ.get("GEMINI_API_KEY"))
engine_name = f"gemini:{GEMINI_MODEL}" if engine.gemini_client else "rules"

app = FastAPI(title="TrueVerdict API")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"chrome-extension://.*",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health():
    return {"status": "ok", "engine": engine_name}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    p = req.product
    product = ProductInfo(
        title=p.title,
        brand=p.brand or None,
        url=p.url,
        platform=p.platform,
        claimed_rating=p.claimedRating,
        total_reviews_count=p.totalReviews,
    )
    reviews = [
        Review(
            id=str(i),
            title=r.title,
            body=r.body,
            rating=r.rating,
            author=r.author,
            date_str=r.dateStr,
            verified_purchase=r.verified,
            is_incentivized=r.incentivized,
        )
        for i, r in enumerate(req.reviews)
    ]
    verdict = engine.evaluate_data(product, reviews)
    return AnalyzeResponse(**verdict.model_dump(), engine=engine_name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8787)))
