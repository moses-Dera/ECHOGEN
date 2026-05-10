"""
Sensor aggregator — auto-discovers all sensor modules via registry,
runs them concurrently, merges results from sensors sharing the same layer.

Adding a new sensor: drop a .py file in sensors/ with fetch() + LAYER constant.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from sensors.registry import discover, list_sources


def fetch_all(min_whale_sol: float = 5_000, news_hours_back: int = 6, target_token: str = "SOL") -> dict:
    sensors = discover()

    def _call(mod):
        import inspect
        sig = inspect.signature(mod.fetch)
        kwargs = {}
        if "min_sol" in sig.parameters:
            kwargs["min_sol"] = min_whale_sol
        if "hours_back" in sig.parameters:
            kwargs["hours_back"] = news_hours_back
        if "target_token" in sig.parameters:
            kwargs["target_token"] = target_token
        return mod.fetch(**kwargs)

    # Collect all results keyed by module name
    raw: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(len(sensors), 1)) as pool:
        futures = {pool.submit(_call, mod): mod for mod in sensors}
        for future in as_completed(futures):
            mod = futures[future]
            try:
                raw[mod.__name__] = future.result()
            except Exception as e:
                raw[mod.__name__] = {
                    "layer": getattr(mod, "LAYER", "unknown"),
                    "source": "error",
                    "error": str(e),
                }

    # Merge sensors that share the same layer
    merged: dict[str, dict] = {}
    for mod_name, data in raw.items():
        layer = data.get("layer", "unknown")

        if layer not in merged:
            merged[layer] = data
            continue

        existing = merged[layer]

        # Skip if new result is fallback/error and existing is live
        if data.get("source") in ("fallback", "error") and existing.get("source") not in ("fallback", "error"):
            continue

        # Merge list fields
        for key in ("crypto_news", "macro_news", "articles", "whale_transfers", "top_pairs", "trending_tokens", "top_movers"):
            if key in data:
                existing.setdefault(key, [])
                existing[key] = _dedup(existing[key] + data[key])

        # Merge unique dict fields (don't overwrite, only add missing keys)
        for key in ("global", "dex", "dex_summary", "cex"):
            if key in data and key not in existing:
                existing[key] = data[key]

        # Enrich sol dict with extra fields from other sources
        if "sol" in data and "sol" in existing:
            for k, v in data["sol"].items():
                if v is not None and existing["sol"].get(k) is None:
                    existing["sol"][k] = v

        # Upgrade source label
        if data.get("source") not in ("fallback", "error"):
            existing_src = existing.get("source", "")
            new_src = data.get("source", "")
            if new_src and new_src not in existing_src:
                existing["source"] = f"{existing_src}+{new_src}".lstrip("+")

    has_live = any(
        v.get("source") not in ("fallback", "error", None)
        for v in merged.values()
    )

    # Build sources metadata with live status
    sources = []
    for meta in list_sources():
        mod_name = meta["module"]
        mod_data = raw.get(mod_name, {})
        sources.append({
            **meta,
            "status": "live" if mod_data.get("source") not in ("fallback", "error", None, "") else mod_data.get("source", "unknown"),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })

    return {
        **merged,
        "sources": sources,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "has_live_data": has_live,
    }


def _dedup(items: list) -> list:
    """Deduplicate news articles by title."""
    seen = set()
    result = []
    for item in items:
        key = str(item.get("title", item.get("signature", id(item))))[:80].lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
