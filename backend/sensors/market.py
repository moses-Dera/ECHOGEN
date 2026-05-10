"""
Layer 2 - Market Momentum
CoinGecko: SOL price, volume, market cap. Birdeye: DEX liquidity (optional).
CoinGecko free tier: no key needed, 30 req/min.
"""
# Registry metadata
LAYER = "market"
LABEL = "CoinGecko + Birdeye (Market)"
SOURCE_URL = "https://coingecko.com"
REQUIRES_KEY = False
KEY_ENV_VAR = None
import os
import requests

_BIRDEYE_KEY = os.getenv("BIRDEYE_API_KEY", "")
_CG_BASE = "https://api.coingecko.com/api/v3"
_BIRDEYE_BASE = "https://public-api.birdeye.so"

# SOL mint address (used for Birdeye lookups)
SOL_MINT = "So11111111111111111111111111111111111111112"

FALLBACK = {
    "layer": "market",
    "source": "fallback",
    "sol": {
        "price_usd": 185.42,
        "market_cap_usd": 87_500_000_000,
        "volume_24h_usd": 3_200_000_000,
        "price_change_24h_pct": -4.2,
        "price_change_1h_pct": -1.1,
    },
    "dex": None,
}


def fetch(target_token: str = "SOL") -> dict:
    target_token = target_token.upper()
    sol = _fetch_coingecko() if target_token == "SOL" else None
    
    mint = SOL_MINT
    if target_token != "SOL":
        resolved_mint = _search_token(target_token)
        if resolved_mint:
            mint = resolved_mint

    dex = _fetch_birdeye(mint) if _BIRDEYE_KEY else None

    return {
        "layer": "market",
        "source": "coingecko+birdeye" if sol and dex else "birdeye" if dex else "coingecko",
        "target_token": target_token,
        "resolved_mint": mint,
        "sol": sol or (FALLBACK["sol"] if target_token == "SOL" else None),
        "dex": dex,
    }


def _search_token(symbol: str) -> str | None:
    """Uses Birdeye search API to find the contract address for a token symbol."""
    try:
        headers = {"X-API-KEY": _BIRDEYE_KEY, "accept": "application/json"}
        resp = requests.get(
            f"{_BIRDEYE_BASE}/defi/v3/search",
            params={"chain": "solana", "keyword": symbol, "target": "token", "sort_by": "volume_24h_usd", "sort_type": "desc"},
            headers=headers,
            timeout=8
        )
        if resp.status_code == 200:
            items = resp.json().get("data", {}).get("items", [])
            for item in items:
                if item.get("type") == "token" and item.get("result"):
                    return item["result"][0].get("address")
    except Exception as e:
        print(f"Token search failed: {e}")
    return None


def _fetch_coingecko() -> dict | None:
    try:
        resp = requests.get(
            f"{_CG_BASE}/coins/solana",
            params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        md = data.get("market_data", {})
        return {
            "price_usd": md.get("current_price", {}).get("usd"),
            "market_cap_usd": md.get("market_cap", {}).get("usd"),
            "volume_24h_usd": md.get("total_volume", {}).get("usd"),
            "price_change_24h_pct": md.get("price_change_percentage_24h"),
            "price_change_1h_pct": md.get("price_change_percentage_1h_in_currency", {}).get("usd"),
            "ath_usd": md.get("ath", {}).get("usd"),
            "ath_change_pct": md.get("ath_change_percentage", {}).get("usd"),
        }
    except Exception:
        return None


def _fetch_birdeye(mint: str) -> dict | None:
    """DEX liquidity, historical trades, and top holders for a specific token mint."""
    try:
        headers = {"X-API-KEY": _BIRDEYE_KEY, "x-chain": "solana", "accept": "application/json"}
        
        # 1. Token Overview
        resp = requests.get(
            f"{_BIRDEYE_BASE}/defi/token_overview",
            params={"address": mint},
            headers=headers,
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        
        # 2. All-Time Trades
        trades_resp = requests.post(
            f"{_BIRDEYE_BASE}/defi/v3/all-time/trades/multiple",
            params={"time_frame": "24h", "ui_amount_mode": "raw"},
            json={"list_address": mint},
            headers=headers,
            timeout=8
        )
        trades_data = {}
        if trades_resp.status_code == 200:
            trades_items = trades_resp.json().get("data", [])
            if trades_items:
                trades_data = trades_items[0]

        # 3. Top Holders
        holders_resp = requests.get(
            f"{_BIRDEYE_BASE}/defi/v3/token/holder",
            params={"address": mint, "offset": 0, "limit": 10, "ui_amount_mode": "scaled"},
            headers=headers,
            timeout=8
        )
        top_holders = []
        if holders_resp.status_code == 200:
            top_holders = [
                {"owner": h.get("owner"), "ui_amount": h.get("ui_amount")}
                for h in holders_resp.json().get("data", {}).get("items", [])
            ]

        # 4. Token Security
        security_resp = requests.get(
            f"{_BIRDEYE_BASE}/defi/token_security",
            params={"address": mint},
            headers=headers,
            timeout=8
        )
        security_data = {}
        if security_resp.status_code == 200:
            security_data = security_resp.json().get("data", {})

        return {
            "liquidity_usd": data.get("liquidity"),
            "volume_24h_usd": data.get("v24hUSD"),
            "price_change_24h_pct": data.get("priceChange24hPercent"),
            "buy_24h": data.get("buy24h"),
            "sell_24h": data.get("sell24h"),
            "unique_wallets_24h": data.get("uniqueWallet24h"),
            "historical_trades": {
                "total_volume_usd": trades_data.get("total_volume_usd"),
                "total_trade": trades_data.get("total_trade")
            },
            "top_10_holders": top_holders,
            "security": {
                "top10HolderPercent": security_data.get("top10HolderPercent"),
                "isTrueToken": security_data.get("isTrueToken"),
                "mutableMetadata": security_data.get("mutableMetadata")
            }
        }
    except Exception as e:
        print(f"Birdeye fetch failed: {e}")
        return None
