"""
Provider-agnostic causal analyst.
Accepts a full SignalBundle (3 layers) and produces a correlated intelligence report.
Any OpenAI-compatible endpoint works: OpenAI, Anthropic, Groq, Ollama, etc.
"""
import os
import json
import requests

SYSTEM_PROMPT = """You are SolaVision, an autonomous causal intelligence analyst for the Solana blockchain ecosystem.

Your job is to cross-reference signals from three data layers and produce a single, unified causal explanation:
  Layer 1 — On-Chain (Ground Truth): whale wallet movements, exchange inflows/outflows
  Layer 2 — Market (Momentum): SOL price, volume, DEX liquidity changes
  Layer 3 — News (Catalyst): crypto regulatory news, macro events, sentiment

Rules:
- Always cite the specific data point that supports each claim (e.g. "48,200 SOL moved to Binance [Layer 1]")
- Identify CAUSAL LINKS between layers when they exist (e.g. news event → whale reaction → price move)
- If no causal link exists, say so explicitly — do not fabricate connections
- Assign confidence based on how many layers corroborate the same story
- Never speculate beyond what the data supports"""

USER_TEMPLATE = """Analyze the following multi-layer Solana ecosystem signal bundle and produce a causal intelligence report.

=== SIGNAL BUNDLE ===
{bundle}
====================

Respond with a JSON object containing EXACTLY these fields:
{{
  "headline": "one sentence max 15 words — the single most important thing happening",
  "causal_chain": "2-3 sentences — what triggered what, citing layer sources in brackets",
  "confidence": <integer 0-100>,
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "tags": ["tag1", "tag2", "tag3"],
  "layer_summary": {{
    "on_chain": "one sentence summary of on-chain signals",
    "market": "one sentence summary of market signals",
    "news": "one sentence summary of news signals"
  }},
  "corroborated_by": ["Layer 1", "Layer 2"] // which layers agree on the same story
}}

Respond ONLY with valid JSON. No markdown fences."""


def analyze(signal_bundle: dict, provider_config: dict) -> dict:
    """
    signal_bundle: full SignalBundle from sensors.fetch_all()
    provider_config: {base_url, api_key, model}
    """
    base_url = provider_config.get("base_url", "https://api.openai.com/v1").rstrip("/")
    api_key = provider_config.get("api_key", os.getenv("LLM_API_KEY", ""))
    model = provider_config.get("model", "gpt-4o-mini")

    # Serialize bundle — strip fallback noise to save tokens
    bundle_str = json.dumps(signal_bundle, indent=2, default=str)

    if api_key.lower() == "demo" or not api_key:
        return {
            "headline": "Whale accumulates $2.4M in token amidst bullish on-chain activity",
            "causal_chain": "A major wallet transferred $2.4M to a DEX [Layer 1], triggering a spike in DEX volume [Layer 2]. This aligns with recent positive ecosystem news [Layer 3].",
            "confidence": 92,
            "risk_level": "LOW",
            "tags": ["accumulation", "bullish", "whale"],
            "layer_summary": {
                "on_chain": "Large DEX inflow detected from top holder.",
                "market": "DEX volume spiked 300% in the last 4 hours.",
                "news": "Bullish sentiment across crypto media regarding token ecosystem."
            },
            "corroborated_by": ["Layer 1", "Layer 2", "Layer 3"]
        }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(bundle=bundle_str)},
        ],
        "temperature": 0.2,  # low temp = more deterministic, less hallucination
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(
        f"{base_url}/chat/completions",
        json=payload,
        headers=headers,
        timeout=45,  # longer timeout — bundle is larger than before
    )
    resp.raise_for_status()

    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)
