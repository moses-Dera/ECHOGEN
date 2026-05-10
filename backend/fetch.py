"""Thin shim — delegates to the sensors package."""
from sensors import fetch_all


def fetch_signal_bundle(**kwargs) -> dict:
    return fetch_all(**kwargs)


# Keep backward-compat name used by main.py during transition
def fetch_large_transfers(min_sol: float = 5_000) -> list[dict]:
    bundle = fetch_all(min_whale_sol=min_sol)
    return bundle["on_chain"].get("whale_transfers", [])
