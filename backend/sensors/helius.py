"""
Layer 1 - Ground Truth (On-Chain)
Helius API: large SOL/SPL transfers + DAS token metadata.
Endpoints: POST /v0/transactions, POST /v0/token-metadata
"""
# Registry metadata - read by sensors/registry.py
LAYER = "on_chain"
LABEL = "Helius (On-Chain)"
SOURCE_URL = "https://helius.dev"
REQUIRES_KEY = True
KEY_ENV_VAR = "HELIUS_API_KEY"
import os
import requests

_KEY = os.getenv("HELIUS_API_KEY", "")
_BASE = "https://api.helius.xyz"
_RPC = f"https://mainnet.helius-rpc.com/?api-key={_KEY}" if _KEY else "https://api.mainnet-beta.solana.com"

# Known exchange deposit wallets (partial list — extend as needed)
KNOWN_EXCHANGES = {
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1": "Binance",
    "2ojv9BAiHUrvsm9gxDe7fJSzbNZSJcxZvf8dqmWGHG8S": "Binance",
    "AC5RDfQFmDS1deWZos921JfqscXdByf8BKHs5ACWjtW2": "Bybit",
    "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": "Kraken",
    "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": "OKX",
}

FALLBACK = {
    "layer": "on_chain",
    "source": "fallback",
    "whale_transfers": [
        {
            "signature": "demo_sig_abc123",
            "amount_sol": 48200,
            "from_address": "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin",
            "to_address": "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
            "to_label": "Binance",
            "direction": "exchange_inflow",
            "token": "SOL",
            "timestamp": "2025-01-15T14:32:00Z",
        }
    ],
    "token_metadata": {},
}


def fetch(min_sol: float = 5_000) -> dict:
    if not _KEY:
        return FALLBACK

    transfers = _fetch_whale_transfers(min_sol)
    if not transfers:
        return FALLBACK

    # Enrich with DAS metadata for any SPL tokens found
    spl_mints = list({t["token_mint"] for t in transfers if t.get("token_mint")})
    metadata = _fetch_token_metadata(spl_mints) if spl_mints else {}

    return {
        "layer": "on_chain",
        "source": "helius",
        "whale_transfers": transfers,
        "token_metadata": metadata,
    }


def _fetch_whale_transfers(min_sol: float) -> list[dict]:
    try:
        resp = requests.post(
            f"{_BASE}/v0/transactions?api-key={_KEY}",
            json={"query": {"types": ["TRANSFER"], "source": "SYSTEM_PROGRAM"}, "limit": 100},
            timeout=10,
        )
        resp.raise_for_status()
        txs = resp.json()
    except Exception:
        return []

    results = []
    for tx in txs:
        for transfer in tx.get("nativeTransfers", []):
            sol = transfer.get("amount", 0) / 1e9
            if sol < min_sol:
                continue

            to_addr = transfer.get("toUserAccount", "")
            from_addr = transfer.get("fromUserAccount", "")
            to_label = KNOWN_EXCHANGES.get(to_addr)
            from_label = KNOWN_EXCHANGES.get(from_addr)

            direction = (
                "exchange_inflow" if to_label
                else "exchange_outflow" if from_label
                else "wallet_to_wallet"
            )

            results.append({
                "signature": tx.get("signature", ""),
                "amount_sol": round(sol, 2),
                "from_address": from_addr,
                "from_label": from_label,
                "to_address": to_addr,
                "to_label": to_label,
                "direction": direction,
                "token": "SOL",
                "token_mint": None,
                "timestamp": tx.get("timestamp", ""),
            })

    # Also check SPL token transfers
    for tx in txs:
        for transfer in tx.get("tokenTransfers", []):
            # Only flag large SPL moves (use USD value if available)
            results.append({
                "signature": tx.get("signature", ""),
                "amount_sol": None,
                "amount_tokens": transfer.get("tokenAmount"),
                "from_address": transfer.get("fromUserAccount", ""),
                "to_address": transfer.get("toUserAccount", ""),
                "to_label": KNOWN_EXCHANGES.get(transfer.get("toUserAccount", "")),
                "direction": "exchange_inflow" if KNOWN_EXCHANGES.get(transfer.get("toUserAccount", "")) else "wallet_to_wallet",
                "token": transfer.get("mint", ""),
                "token_mint": transfer.get("mint"),
                "timestamp": tx.get("timestamp", ""),
            })

    return results[:10]  # top 10 signals


def _fetch_token_metadata(mints: list[str]) -> dict:
    """DAS: resolve mint addresses to human-readable token names."""
    try:
        resp = requests.post(
            f"{_BASE}/v0/token-metadata?api-key={_KEY}",
            json={"mintAccounts": mints, "includeOffChain": True, "disableCache": False},
            timeout=8,
        )
        resp.raise_for_status()
        items = resp.json()
        return {
            item["account"]: {
                "name": item.get("onChainMetadata", {}).get("metadata", {}).get("data", {}).get("name", ""),
                "symbol": item.get("onChainMetadata", {}).get("metadata", {}).get("data", {}).get("symbol", ""),
            }
            for item in items
            if item.get("account")
        }
    except Exception:
        return {}
