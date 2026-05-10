import requests

# Registry metadata
LAYER = "market"
LABEL = "DexScreener (Solana DEX)"
SOURCE_URL = "https://dexscreener.com"
REQUIRES_KEY = False
KEY_ENV_VAR = None

# Completely free, no API key needed
# Rate limit: 300 req/min
# Docs: https://docs.dexscreener.com/api/reference
_BASE = "https://api.dexscreener.com"

# Top Solana DEX pools to monitor
WATCHED_PAIRS = [
    "So11111111111111111111111111111111111111112",  # SOL
]


def fetch() -> dict:
    sol_pairs = _fetch_sol_pairs()
    trending = _fetch_trending_solana()

    if not sol_pairs and not trending:
        return {"layer": LAYER, "source": "fallback", "pairs": [], "trending": []}

    # Aggregate liquidity and volume across top SOL pairs
    total_liquidity = sum(p.get("liquidity_usd", 0) or 0 for p in sol_pairs)
    total_volume_24h = sum(p.get("volume_24h_usd", 0) or 0 for p in sol_pairs)
    total_buys = sum(p.get("buys_24h", 0) or 0 for p in sol_pairs)
    total_sells = sum(p.get("sells_24h", 0) or 0 for p in sol_pairs)

    buy_sell_ratio = round(total_buys / total_sells, 3) if total_sells > 0 else None
    pressure = (
        "buy_pressure" if buy_sell_ratio and buy_sell_ratio > 1.1
        else "sell_pressure" if buy_sell_ratio and buy_sell_ratio < 0.9
        else "neutral"
    )

    return {
        "layer": LAYER,
        "source": "dexscreener",
        "dex_summary": {
            "total_liquidity_usd": round(total_liquidity),
            "total_volume_24h_usd": round(total_volume_24h),
            "total_buys_24h": total_buys,
            "total_sells_24h": total_sells,
            "buy_sell_ratio": buy_sell_ratio,
            "market_pressure": pressure,
        },
        "top_pairs": sol_pairs[:5],
        "trending_tokens": trending[:10],
    }


def _fetch_sol_pairs() -> list[dict]:
    try:
        resp = requests.get(
            f"{_BASE}/token-pairs/v1/solana/So11111111111111111111111111111111111111112",
            timeout=8,
        )
        if not resp.ok:
            return []

        # API returns a list directly, not {pairs: [...]}
        data = resp.json()
        pairs = data if isinstance(data, list) else data.get("pairs", [])
        results = []

        for p in sorted(pairs, key=lambda x: x.get("volume", {}).get("h24", 0) or 0, reverse=True)[:10]:
            price_change = p.get("priceChange", {})
            volume = p.get("volume", {})
            liquidity = p.get("liquidity", {})
            txns = p.get("txns", {}).get("h24", {})

            results.append({
                "pair": f"{p.get('baseToken', {}).get('symbol', '?')}/{p.get('quoteToken', {}).get('symbol', '?')}",
                "dex": p.get("dexId", ""),
                "price_usd": p.get("priceUsd"),
                "price_change_5m_pct": price_change.get("m5"),
                "price_change_1h_pct": price_change.get("h1"),
                "price_change_24h_pct": price_change.get("h24"),
                "volume_24h_usd": volume.get("h24"),
                "liquidity_usd": liquidity.get("usd"),
                "buys_24h": txns.get("buys"),
                "sells_24h": txns.get("sells"),
                "pair_address": p.get("pairAddress", ""),
                "url": p.get("url", ""),
            })

        return results
    except Exception:
        return []


def _fetch_trending_solana() -> list[dict]:
    """Top trending token pairs on Solana right now."""
    try:
        resp = requests.get(
            f"{_BASE}/token-boosts/top/v1",
            timeout=8,
        )
        if not resp.ok:
            return []

        tokens = resp.json() if isinstance(resp.json(), list) else []
        solana_tokens = [t for t in tokens if t.get("chainId") == "solana"]

        return [
            {
                "token": t.get("tokenAddress", ""),
                "description": (t.get("description") or "")[:100],
                "url": t.get("url", ""),
                "links": t.get("links", []),
            }
            for t in solana_tokens[:10]
        ]
    except Exception:
        return []
