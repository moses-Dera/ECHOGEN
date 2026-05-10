import os
import requests
from datetime import datetime, timezone, timedelta

# Registry metadata
LAYER = "market"
LABEL = "CoinMarketCap (Global Market)"
SOURCE_URL = "https://coinmarketcap.com"
REQUIRES_KEY = True
KEY_ENV_VAR = "CMC_API_KEY"

# Free Basic plan: 10,000 credits/month
# Endpoints used:
#   /v1/cryptocurrency/quotes/latest        — SOL current price + metadata
#   /v1/cryptocurrency/listings/latest      — top movers, Solana ecosystem tokens
#   /v1/cryptocurrency/listings/historical  — 7-day-ago snapshot for trend comparison
#   /v1/global-metrics/quotes/latest        — BTC dominance, total market cap, DeFi vol
_BASE = "https://pro-api.coinmarketcap.com"


def fetch() -> dict:
    api_key = os.getenv("CMC_API_KEY", "")
    if not api_key:
        return {"layer": LAYER, "source": "fallback", "sol": None, "global": None, "top_movers": [], "sol_ecosystem": [], "historical_context": None}

    headers = {"X-CMC_PRO_API_KEY": api_key, "Accept": "application/json"}

    sol = _fetch_sol(headers)
    global_metrics = _fetch_global(headers)
    top_movers = _fetch_top_movers(headers)
    sol_ecosystem = _fetch_sol_ecosystem(headers)
    historical = _fetch_historical_context(headers)

    if not sol:
        return {"layer": LAYER, "source": "fallback", "sol": None, "global": None, "top_movers": [], "sol_ecosystem": [], "historical_context": None}

    return {
        "layer": LAYER,
        "source": "coinmarketcap",
        "sol": sol,
        "global": global_metrics,
        "top_movers": top_movers,
        "sol_ecosystem": sol_ecosystem,
        "historical_context": historical,
    }


def _fetch_sol(headers: dict) -> dict | None:
    try:
        resp = requests.get(
            f"{_BASE}/v1/cryptocurrency/quotes/latest",
            params={"symbol": "SOL", "convert": "USD"},
            headers=headers,
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()["data"]["SOL"]
        q = data["quote"]["USD"]
        return {
            "price_usd": q.get("price"),
            "market_cap_usd": q.get("market_cap"),
            "volume_24h_usd": q.get("volume_24h"),
            "volume_change_24h_pct": q.get("volume_change_24h"),
            "price_change_1h_pct": q.get("percent_change_1h"),
            "price_change_24h_pct": q.get("percent_change_24h"),
            "price_change_7d_pct": q.get("percent_change_7d"),
            "price_change_30d_pct": q.get("percent_change_30d"),
            "market_cap_dominance_pct": q.get("market_cap_dominance"),
            "fully_diluted_mcap": q.get("fully_diluted_market_cap"),
            "cmc_rank": data.get("cmc_rank"),
            "circulating_supply": data.get("circulating_supply"),
            "max_supply": data.get("max_supply"),
            "last_updated": q.get("last_updated"),
        }
    except Exception:
        return None


def _fetch_global(headers: dict) -> dict | None:
    try:
        resp = requests.get(
            f"{_BASE}/v1/global-metrics/quotes/latest",
            headers=headers,
            timeout=8,
        )
        resp.raise_for_status()
        gm = resp.json()["data"]
        q = gm["quote"]["USD"]

        btc_dom = gm.get("btc_dominance", 0)
        eth_dom = gm.get("eth_dominance", 0)
        alt_dom = round(100 - btc_dom - eth_dom, 2)

        regime = (
            "risk_off"   if btc_dom > 62 else
            "alt_season" if alt_dom > 35 else
            "neutral"
        )

        return {
            "total_market_cap_usd": q.get("total_market_cap"),
            "total_volume_24h_usd": q.get("total_volume_24h"),
            "total_volume_change_24h_pct": q.get("total_volume_24h_reported"),
            "btc_dominance_pct": btc_dom,
            "eth_dominance_pct": eth_dom,
            "altcoin_dominance_pct": alt_dom,
            "active_cryptocurrencies": gm.get("active_cryptocurrencies"),
            "active_exchanges": gm.get("active_exchanges"),
            "market_regime": regime,
            "defi_volume_24h_usd": q.get("defi_volume_24h"),
            "defi_market_cap_usd": q.get("defi_market_cap"),
            "stablecoin_volume_24h_usd": q.get("stablecoin_volume_24h"),
            "stablecoin_market_cap_usd": q.get("stablecoin_market_cap"),
        }
    except Exception:
        return None


def _fetch_top_movers(headers: dict) -> list[dict]:
    """Top 5 gainers + top 5 losers from top-100 by market cap."""
    try:
        resp = requests.get(
            f"{_BASE}/v1/cryptocurrency/listings/latest",
            params={
                "start": 1,
                "limit": 100,
                "convert": "USD",
                "sort": "market_cap",
                "sort_dir": "desc",
                "aux": "cmc_rank",
            },
            headers=headers,
            timeout=8,
        )
        resp.raise_for_status()
        coins = resp.json()["data"]

        def fmt(c: dict, direction: str) -> dict:
            q = c["quote"]["USD"]
            return {
                "symbol": c["symbol"],
                "name": c["name"],
                "cmc_rank": c.get("cmc_rank"),
                "price_usd": q.get("price"),
                "change_24h_pct": q.get("percent_change_24h"),
                "change_7d_pct": q.get("percent_change_7d"),
                "volume_24h_usd": q.get("volume_24h"),
                "market_cap_usd": q.get("market_cap"),
                "direction": direction,
            }

        sorted_by_change = sorted(
            coins,
            key=lambda x: x["quote"]["USD"].get("percent_change_24h") or 0,
            reverse=True,
        )
        gainers = [fmt(c, "gainer") for c in sorted_by_change[:5]]
        losers  = [fmt(c, "loser")  for c in sorted_by_change[-5:]]
        return gainers + losers
    except Exception:
        return []


def _fetch_sol_ecosystem(headers: dict) -> list[dict]:
    """
    Top Solana-ecosystem tokens by market cap using the 'solana-ecosystem' tag.
    Gives the AI context on whether SOL ecosystem tokens are moving with or
    against SOL itself — divergence is a signal.
    """
    try:
        resp = requests.get(
            f"{_BASE}/v1/cryptocurrency/listings/latest",
            params={
                "start": 1,
                "limit": 20,
                "convert": "USD",
                "sort": "market_cap",
                "sort_dir": "desc",
                "tag": "solana-ecosystem",
                "aux": "cmc_rank,tags",
            },
            headers=headers,
            timeout=8,
        )
        resp.raise_for_status()
        coins = resp.json()["data"]

        return [
            {
                "symbol": c["symbol"],
                "name": c["name"],
                "cmc_rank": c.get("cmc_rank"),
                "price_usd": c["quote"]["USD"].get("price"),
                "change_24h_pct": c["quote"]["USD"].get("percent_change_24h"),
                "change_7d_pct": c["quote"]["USD"].get("percent_change_7d"),
                "volume_24h_usd": c["quote"]["USD"].get("volume_24h"),
                "market_cap_usd": c["quote"]["USD"].get("market_cap"),
            }
            for c in coins
        ]
    except Exception:
        return []


def _fetch_historical_context(headers: dict) -> dict | None:
    """
    Compare today's SOL rank/price against 7 days ago using listings/historical.
    Rank movement (e.g. #9 → #7) is a strong signal the AI can cite.
    """
    date_7d_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        resp = requests.get(
            f"{_BASE}/v1/cryptocurrency/listings/historical",
            params={
                "date": date_7d_ago,
                "start": 1,
                "limit": 20,
                "convert": "USD",
                "sort": "cmc_rank",
                "aux": "cmc_rank",
            },
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        coins = resp.json()["data"]

        sol_7d = next((c for c in coins if c["symbol"] == "SOL"), None)
        if not sol_7d:
            return None

        q = sol_7d["quote"]["USD"]
        return {
            "date": date_7d_ago,
            "sol_rank_7d_ago": sol_7d.get("cmc_rank"),
            "sol_price_7d_ago": q.get("price"),
            "sol_mcap_7d_ago": q.get("market_cap"),
            "sol_volume_7d_ago": q.get("volume_24h"),
        }
    except Exception:
        return None
