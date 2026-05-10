import os
import requests

# Registry metadata
LAYER = "news"
LABEL = "NewsAPI.ai (ML-Enriched, 150k+ Sources)"
SOURCE_URL = "https://newsapi.ai"
REQUIRES_KEY = True
KEY_ENV_VAR = "NEWSAPI_AI_KEY"

# Free tier: 2,000 articles/day
# Sign up: https://newsapi.ai  (powered by EventRegistry)
# Sentiment: float -1.0 (very negative) to +1.0 (very positive)
# Concept search: finds articles mentioning Solana by concept, not just keyword
_BASE = "https://eventregistry.org/api/v1"


def fetch(hours_back: int = 6) -> dict:
    api_key = os.getenv("NEWSAPI_AI_KEY", "")
    if not api_key:
        return {"layer": LAYER, "source": "fallback", "articles": [], "crypto_news": [], "macro_news": []}

    articles = []

    # Query 1: Solana keyword articles, sorted by date
    try:
        resp = requests.get(
            f"{_BASE}/article/getArticles",
            json={
                "apiKey": api_key,
                "keyword": "Solana",
                "keywordSearchMode": "simple",
                "lang": "eng",
                "articlesCount": 10,
                "articlesSortBy": "date",
                "articlesSortByAsc": False,
                "resultType": "articles",
                "dataType": ["news", "blog"],
                "articleBodyLen": 200,
            },
            timeout=10,
        )
        if resp.ok:
            for a in resp.json().get("articles", {}).get("results", []):
                articles.append(_fmt(a, "solana"))
    except Exception:
        pass

    # Query 2: Crypto regulation / macro events
    try:
        resp = requests.get(
            f"{_BASE}/article/getArticles",
            json={
                "apiKey": api_key,
                "keyword": "crypto regulation OR SEC blockchain OR stablecoin OR Federal Reserve crypto",
                "keywordSearchMode": "simple",
                "lang": "eng",
                "articlesCount": 5,
                "articlesSortBy": "date",
                "articlesSortByAsc": False,
                "resultType": "articles",
                "dataType": ["news"],
                "articleBodyLen": 200,
            },
            timeout=10,
        )
        if resp.ok:
            for a in resp.json().get("articles", {}).get("results", []):
                articles.append(_fmt(a, "macro"))
    except Exception:
        pass

    if not articles:
        return {"layer": LAYER, "source": "fallback", "articles": [], "crypto_news": [], "macro_news": []}

    crypto = [a for a in articles if a["category"] == "solana"]
    macro = [a for a in articles if a["category"] == "macro"]

    return {
        "layer": LAYER,
        "source": "newsapi_ai",
        "articles": articles,
        "crypto_news": crypto,
        "macro_news": macro,
    }


def _fmt(a: dict, category: str) -> dict:
    # Sentiment is a float: -1.0 to +1.0
    raw = a.get("sentiment") or 0.0
    sentiment = (
        "positive" if raw > 0.1
        else "negative" if raw < -0.1
        else "neutral"
    )
    source = a.get("source", {})
    return {
        "title": a.get("title", ""),
        "url": a.get("url", ""),
        "original_url": a.get("url", ""),
        "source": source.get("title", "") if isinstance(source, dict) else str(source),
        "source_domain": source.get("uri", "") if isinstance(source, dict) else "",
        "published_at": a.get("dateTime", a.get("date", "")),
        "description": (a.get("body") or a.get("description") or "")[:300],
        "sentiment": sentiment,
        "sentiment_score": round(float(raw), 3),
        "importance": "high" if abs(raw) > 0.4 else "medium",
        "category": category,
    }
