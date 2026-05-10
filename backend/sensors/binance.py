import requests

# Registry metadata
LAYER = "market"
LABEL = "Binance (CEX SOL/USDT)"
SOURCE_URL = "https://binance.com"
REQUIRES_KEY = False
KEY_ENV_VAR = None

# Binance public REST API — no key needed for market data
# Rate limit: 1200 req/min weight
# Note: may be DNS-blocked in some regions — falls back gracefully
# Docs: https://binance-docs.github.io/apidocs/spot/en/
_BASE = "https://api.binance.com/api/v3"
_FAPI = "https://fapi.binance.com/fapi/v1"  # futures — funding rate
# Fallback: use api.binance.us for US-region or api3.binance.com for redundancy
_BASE_ALT = "https://api3.binance.com/api/v3"

SYMBOL = "SOLUSDT"


def fetch() -> dict:
    ticker = _fetch_ticker()
    depth = _fetch_order_book_depth()
    funding = _fetch_funding_rate()

    if not ticker:
        return {"layer": LAYER, "source": "fallback", "cex": None}

    # Derive CEX signal
    bid_ask_spread_pct = None
    if depth and depth.get("best_bid") and depth.get("best_ask"):
        spread = depth["best_ask"] - depth["best_bid"]
        bid_ask_spread_pct = round(spread / depth["best_bid"] * 100, 4)

    # Funding rate signal: positive = longs paying shorts (bullish bias)
    # negative = shorts paying longs (bearish bias)
    funding_signal = None
    if funding is not None:
        funding_signal = (
            "bullish_bias" if funding > 0.0001
            else "bearish_bias" if funding < -0.0001
            else "neutral"
        )

    return {
        "layer": LAYER,
        "source": "binance",
        "cex": {
            "symbol": SYMBOL,
            "price_usd": ticker.get("price_usd"),
            "price_change_24h_pct": ticker.get("price_change_pct"),
            "volume_24h_sol": ticker.get("volume_24h"),
            "volume_24h_usd": ticker.get("volume_24h_usd"),
            "high_24h": ticker.get("high_24h"),
            "low_24h": ticker.get("low_24h"),
            "trades_24h": ticker.get("trades_24h"),
            "bid_ask_spread_pct": bid_ask_spread_pct,
            "order_book": depth,
            "funding_rate": funding,
            "funding_signal": funding_signal,
        },
    }


def _fetch_ticker() -> dict | None:
    for base in [_BASE, _BASE_ALT]:
        try:
            resp = requests.get(
                f"{base}/ticker/24hr",
                params={"symbol": SYMBOL},
                timeout=6,
            )
            if not resp.ok:
                continue
            d = resp.json()
            return {
                "price_usd": float(d.get("lastPrice", 0)),
                "price_change_pct": float(d.get("priceChangePercent", 0)),
                "volume_24h": float(d.get("volume", 0)),
                "volume_24h_usd": float(d.get("quoteVolume", 0)),
                "high_24h": float(d.get("highPrice", 0)),
                "low_24h": float(d.get("lowPrice", 0)),
                "trades_24h": int(d.get("count", 0)),
            }
        except Exception:
            continue
    return None


def _fetch_order_book_depth() -> dict | None:
    """Top 5 bids/asks — shows immediate buy/sell wall pressure."""
    try:
        resp = requests.get(
            f"{_BASE}/depth",
            params={"symbol": SYMBOL, "limit": 5},
            timeout=6,
        )
        resp.raise_for_status()
        d = resp.json()
        bids = [[float(p), float(q)] for p, q in d.get("bids", [])]
        asks = [[float(p), float(q)] for p, q in d.get("asks", [])]

        bid_volume = sum(p * q for p, q in bids)
        ask_volume = sum(p * q for p, q in asks)

        return {
            "best_bid": bids[0][0] if bids else None,
            "best_ask": asks[0][0] if asks else None,
            "bid_wall_usd": round(bid_volume),
            "ask_wall_usd": round(ask_volume),
            "wall_pressure": "buy_wall" if bid_volume > ask_volume * 1.2 else "sell_wall" if ask_volume > bid_volume * 1.2 else "balanced",
        }
    except Exception:
        return None


def _fetch_funding_rate() -> float | None:
    """Perpetual futures funding rate — key sentiment indicator."""
    try:
        resp = requests.get(
            f"{_FAPI}/fundingRate",
            params={"symbol": SYMBOL, "limit": 1},
            timeout=6,
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0].get("fundingRate", 0))
        return None
    except Exception:
        return None
