import os
import requests
from datetime import datetime, timezone, timedelta

# Registry metadata - read by sensors/registry.py
LAYER = "news"
LABEL = "CryptoPanic + NewsAPI (News)"
SOURCE_URL = "https://cryptopanic.com"
REQUIRES_KEY = False
KEY_ENV_VAR = "CRYPTOPANIC_API_KEY"

_NEWS_BASE = "https://newsapi.org/v2"

FALLBACK = {
    "layer": "news",
    "source": "fallback",
    "crypto_news": [
        {
            "title": "Solana network activity surges as DeFi volumes hit monthly high",
            "url": "https://cryptopanic.com",
            "sentiment": "positive",
            "importance": "medium",
            "votes_bullish": 12,
            "votes_bearish": 3,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "source": "CryptoPanic (fallback)",
            "original_url": "https://cryptopanic.com",
        }
    ],
    "macro_news": [],
}


def fetch(hours_back: int = 6) -> dict:
    # All env reads are lazy here — picks up dotenv loaded by main.py
    news_key = os.getenv("NEWS_API_KEY", "")
    cp_token = os.getenv("CRYPTOPANIC_API_KEY", "")

    crypto = _fetch_cryptopanic(hours_back, cp_token)
    macro = _fetch_newsapi(hours_back, news_key) if news_key else []

    if not crypto and not macro:
        return FALLBACK

    source_parts = []
    if crypto:
        source_parts.append("cryptopanic")
    if macro:
        source_parts.append("newsapi")

    return {
        "layer": "news",
        "source": "+".join(source_parts),
        "crypto_news": crypto or [],
        "macro_news": macro,
    }


def _fetch_cryptopanic(hours_back: int, token: str) -> list[dict]:
    if not token:
        return []

    plan = os.getenv("CRYPTOPANIC_PLAN", "developer")
    base = f"https://cryptopanic.com/api/{plan}/v2"

    params = {
        "auth_token": token,
        "currencies": "SOL",
        "filter": "important",
        "kind": "news",
        "public": "true",
        "regions": "en",
    }

    try:
        resp = requests.get(f"{base}/posts/", params=params, timeout=8)
        if resp.status_code in (401, 403, 429):
            return []
        resp.raise_for_status()
        posts = resp.json().get("results", [])
    except Exception:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    results = []

    for post in posts:
        published = post.get("published_at", "")
        try:
            pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if pub_dt < cutoff:
                continue
        except Exception:
            pass

        votes = post.get("votes", {})
        bullish = votes.get("positive", 0)
        bearish = votes.get("negative", 0)
        important = votes.get("important", 0)
        total = bullish + bearish + important

        results.append({
            "title": post.get("title", ""),
            "url": post.get("url", ""),
            "original_url": post.get("original_url", ""),
            "sentiment": "positive" if bullish > bearish else "negative" if bearish > bullish else "neutral",
            "importance": "high" if total > 10 else "medium" if total > 3 else "low",
            "votes_bullish": bullish,
            "votes_bearish": bearish,
            "votes_important": important,
            "panic_score": post.get("panic_score"),
            "published_at": published,
            "source": post.get("source", {}).get("title", ""),
            "source_domain": post.get("source", {}).get("domain", ""),
        })

    return results[:8]


def _fetch_newsapi(hours_back: int, api_key: str) -> list[dict]:
    # Note: NewsAPI free plan restricts 'from' date to articles older than 1 month.
    # We omit 'from' and sort by publishedAt to get the most recent available articles.
    results = []

    # Solana-specific news
    try:
        resp = requests.get(
            f"{_NEWS_BASE}/everything",
            params={
                "q": "Solana OR SOL blockchain",
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 5,
                "apiKey": api_key,
            },
            timeout=8,
        )
        if resp.ok:
            for a in resp.json().get("articles", []):
                results.append(_fmt(a, "solana"))
    except Exception:
        pass

    # Macro events that move crypto markets
    try:
        resp = requests.get(
            f"{_NEWS_BASE}/everything",
            params={
                "q": "(Federal Reserve OR SEC OR crypto regulation OR stablecoin) AND (crypto OR bitcoin OR blockchain)",
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": 3,
                "apiKey": api_key,
            },
            timeout=8,
        )
        if resp.ok:
            for a in resp.json().get("articles", []):
                results.append(_fmt(a, "macro"))
    except Exception:
        pass

    return results


def _fmt(a: dict, category: str) -> dict:
    return {
        "title": a.get("title", ""),
        "url": a.get("url", ""),
        "original_url": a.get("url", ""),
        "source": a.get("source", {}).get("name", ""),
        "published_at": a.get("publishedAt", ""),
        "description": (a.get("description") or "")[:200],
        "category": category,
        "sentiment": "neutral",
        "importance": "medium",
    }
