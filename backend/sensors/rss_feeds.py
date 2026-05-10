import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone

# Registry metadata
LAYER = "news"
LABEL = "RSS Feeds (CoinDesk, Decrypt, Cointelegraph)"
SOURCE_URL = "https://coindesk.com"
REQUIRES_KEY = False
KEY_ENV_VAR = None

# Zero API key needed — public RSS feeds
# These are the most reliable free crypto news sources
RSS_FEEDS = [
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "category": "crypto",
    },
    {
        "name": "Decrypt",
        "url": "https://decrypt.co/feed",
        "category": "crypto",
    },
    {
        "name": "Cointelegraph",
        "url": "https://cointelegraph.com/rss",
        "category": "crypto",
    },
    {
        "name": "The Block",
        "url": "https://www.theblock.co/rss.xml",
        "category": "crypto",
    },
    {
        "name": "Bitcoin Magazine",
        "url": "https://bitcoinmagazine.com/.rss/full/",
        "category": "crypto",
    },
]

# Keywords to filter for Solana relevance
SOLANA_KEYWORDS = {
    "solana", "sol", "raydium", "jupiter", "marinade",
    "phantom", "serum", "pyth", "jito", "drift",
}


def fetch(hours_back: int = 6) -> dict:
    articles = []

    for feed in RSS_FEEDS:
        try:
            resp = requests.get(
                feed["url"],
                headers={"User-Agent": "EchoGen/1.0 (Solana Intelligence Oracle)"},
                timeout=6,
            )
            if not resp.ok:
                continue

            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if channel is None:
                continue

            for item in channel.findall("item")[:5]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub_date = (item.findtext("pubDate") or "").strip()
                description = (item.findtext("description") or "").strip()[:200]

                # Filter: only include if Solana-relevant
                text_lower = (title + " " + description).lower()
                is_solana = any(kw in text_lower for kw in SOLANA_KEYWORDS)
                # Also include high-impact macro crypto news
                is_macro = any(kw in text_lower for kw in {
                    "sec", "federal reserve", "regulation", "etf", "bitcoin", "ethereum",
                    "crypto", "blockchain", "defi", "stablecoin",
                })

                if not (is_solana or is_macro):
                    continue

                articles.append({
                    "title": title,
                    "url": link,
                    "original_url": link,
                    "source": feed["name"],
                    "published_at": pub_date,
                    "description": description,
                    "sentiment": "neutral",  # RSS has no sentiment — AI infers
                    "importance": "high" if is_solana else "medium",
                    "category": "solana" if is_solana else "macro",
                    "ai_summarized": False,
                })

        except Exception:
            continue

    if not articles:
        return {"layer": LAYER, "source": "fallback", "articles": []}

    # Deduplicate by title
    seen = set()
    unique = []
    for a in articles:
        key = a["title"][:60].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return {
        "layer": LAYER,
        "source": "rss",
        "articles": unique[:15],
        "crypto_news": [a for a in unique if a["category"] == "solana"][:8],
        "macro_news": [a for a in unique if a["category"] == "macro"][:5],
    }
