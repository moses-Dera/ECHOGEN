import os
import requests

# Registry metadata
LAYER = "news"
LABEL = "NewsData.io (Crypto)"
SOURCE_URL = "https://newsdata.io"
REQUIRES_KEY = True
KEY_ENV_VAR = "NEWSDATA_API_KEY"

# Free tier: 200 credits/day, 10 results/request
# Sentiment field: paid plans only — handled gracefully below
# Endpoints: /latest (general), /crypto (crypto-specific)
# Docs: https://newsdata.io/documentation
_BASE = "https://newsdata.io/api/1"

_PAID_SENTINEL = "ONLY AVAILABLE IN PROFESSIONAL AND CORPORATE PLANS"


def fetch(hours_back: int = 6) -> dict:
    api_key = os.getenv("NEWSDATA_API_KEY", "")
    if not api_key:
        return {"layer": LAYER, "source": "fallback", "articles": [], "crypto_news": [], "macro_news": []}

    articles = []

    # /crypto — dedicated crypto endpoint, Solana-filtered
    try:
        resp = requests.get(
            f"{_BASE}/crypto",
            params={"apikey": api_key, "q": "Solana OR SOL", "language": "en", "size": 10},
            timeout=8,
        )
        if resp.ok:
            for a in resp.json().get("results", []):
                articles.append(_fmt(a, "solana"))
    except Exception:
        pass

    # /latest — broader crypto + macro news
    try:
        resp = requests.get(
            f"{_BASE}/latest",
            params={
                "apikey": api_key,
                "q": "crypto regulation OR SEC blockchain OR stablecoin",
                "language": "en",
                "category": "business,technology",
                "size": 5,
            },
            timeout=8,
        )
        if resp.ok:
            for a in resp.json().get("results", []):
                articles.append(_fmt(a, "macro"))
    except Exception:
        pass

    if not articles:
        return {"layer": LAYER, "source": "fallback", "articles": [], "crypto_news": [], "macro_news": []}

    crypto = [a for a in articles if a["category"] == "solana"]
    macro = [a for a in articles if a["category"] == "macro"]

    return {
        "layer": LAYER,
        "source": "newsdata",
        "articles": articles,
        "crypto_news": crypto,
        "macro_news": macro,
    }


def _fmt(a: dict, category: str) -> dict:
    # Sentiment is paid-only — falls back to "neutral" on free tier
    raw_sentiment = a.get("sentiment", "")
    sentiment = (
        raw_sentiment.lower()
        if raw_sentiment and raw_sentiment != _PAID_SENTINEL
        else "neutral"
    )
    return {
        "title": a.get("title", ""),
        "url": a.get("link", ""),
        "original_url": a.get("source_url", a.get("link", "")),
        "source": a.get("source_name", ""),
        "published_at": a.get("pubDate", ""),
        "description": (a.get("description") or "")[:200],
        "sentiment": sentiment,
        "sentiment_paid_only": raw_sentiment == _PAID_SENTINEL,
        "importance": "medium",
        "category": category,
        "keywords": (a.get("keywords") or [])[:5],
    }
