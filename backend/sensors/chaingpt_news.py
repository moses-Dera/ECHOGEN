import os
import requests

# Registry metadata
LAYER = "news"
LABEL = "ChainGPT AI News"
SOURCE_URL = "https://news.chaingpt.org"
REQUIRES_KEY = True
KEY_ENV_VAR = "CHAINGPT_API_KEY"

# Docs: https://docs.chaingpt.org/the-ecosystem/ai-news
# Free tier: available with API key from app.chaingpt.org
# Endpoint returns AI-summarized, cross-verified crypto news
_BASE = "https://news.chaingpt.org/api"


def fetch(hours_back: int = 6) -> dict:
    api_key = os.getenv("CHAINGPT_API_KEY", "")
    if not api_key:
        return {"layer": LAYER, "source": "fallback", "articles": []}

    articles = []

    try:
        resp = requests.get(
            f"{_BASE}/v1/news",
            params={
                "search": "Solana",
                "limit": 10,
                "sortBy": "publishedAt",
                "order": "DESC",
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=8,
        )
        if resp.ok:
            data = resp.json()
            # ChainGPT returns {data: [...]} or {news: [...]} depending on version
            items = data.get("data") or data.get("news") or data.get("results") or []
            for a in items:
                articles.append(_fmt(a))
    except Exception:
        pass

    if not articles:
        return {"layer": LAYER, "source": "fallback", "articles": []}

    return {
        "layer": LAYER,
        "source": "chaingpt",
        "articles": articles,
        "crypto_news": articles,
        "macro_news": [],
    }


def _fmt(a: dict) -> dict:
    return {
        "title": a.get("title", ""),
        "url": a.get("url") or a.get("link", ""),
        "original_url": a.get("originalUrl") or a.get("url", ""),
        "source": a.get("source") or a.get("sourceName", "ChainGPT"),
        "published_at": a.get("publishedAt") or a.get("date", ""),
        # ChainGPT provides AI summary — use as description
        "description": (a.get("summary") or a.get("description") or "")[:300],
        "sentiment": a.get("sentiment", "neutral"),
        "importance": "medium",
        "category": "crypto",
        "ai_summarized": True,
    }
