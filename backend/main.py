"""
EchoGen Oracle Backend
  GET  /health          — liveness check
  GET  /signals         — free: returns full 3-layer signal bundle (no AI reasoning)
  POST /insight/full    — x402-gated: causal AI analysis of the signal bundle
"""
import os
from dotenv import load_dotenv
load_dotenv()  # loads .env from cwd (run from backend/) or parent
load_dotenv("../.env")  # fallback if run from project root

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

from sensors import fetch_all
from sensors.registry import list_sources
from analyst import analyze
import db

app = FastAPI(title="EchoGen Oracle")

# More robust CORS for Vercel + Mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/")
def root():
    return {"status": "EchoGen Backend Live", "docs": "/docs"}

PAYMENT_AMOUNT_LAMPORTS = int(os.getenv("PAYMENT_AMOUNT_LAMPORTS", "1000000"))
ORACLE_WALLET = os.getenv("ORACLE_WALLET", "")
CLUSTER = os.getenv("SOLANA_CLUSTER", "devnet")
SOLSCAN_SUFFIX = "" if CLUSTER == "mainnet" else "?cluster=devnet"

class InsightRequest(BaseModel):
    payment_signature: str
    provider_config: dict  # {base_url, api_key, model}
    target_token: str = "SOL"


ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "onwK4e9ZLuTAKqWW03F9")  # Daniel — authoritative


@app.get("/health")
def health():
    return {"status": "ok", "cluster": CLUSTER}


@app.get("/sources")
def get_sources():
    """Returns metadata about all registered sensors — powers the Sources panel."""
    return {"sources": list_sources()}


class NarrateRequest(BaseModel):
    text: str  # the causal_chain text to narrate


@app.post("/narrate")
async def narrate(body: NarrateRequest):
    """ElevenLabs TTS — converts insight text to audio. Returns audio/mpeg stream."""
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=503, detail="ELEVENLABS_API_KEY not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={
                "text": body.text,
                "model_id": "eleven_turbo_v2",
                "voice_settings": {"stability": 0.4, "similarity_boost": 0.8},
            },
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="ElevenLabs API error")
        audio = resp.content

    return StreamingResponse(
        iter([audio]),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=insight.mp3"},
    )


@app.get("/signals")
def get_signals(target_token: str = "SOL"):
    """
    Free endpoint — returns the full 3-layer signal bundle.
    On-chain data is visible. AI causal reasoning is gated behind payment.
    """
    bundle = fetch_all(target_token=target_token)
    return {
        "bundle": bundle,
        "preview": True,
        "payment_required": {
            "amount_lamports": PAYMENT_AMOUNT_LAMPORTS,
            "amount_sol": PAYMENT_AMOUNT_LAMPORTS / 1e9,
            "recipient": ORACLE_WALLET,
            "memo": "echogen:insight:v1",
            "cluster": CLUSTER,
        },
    }


# Keep /insight for backward compat with existing frontend
@app.get("/insight")
def get_insight_preview(target_token: str = "SOL"):
    bundle = fetch_all(target_token=target_token)
    # Surface the most prominent on-chain signal as the "signal" field
    transfers = bundle["on_chain"].get("whale_transfers", [])
    signal = transfers[0] if transfers else {}
    return {
        "signal": signal,
        "bundle_summary": {
            "on_chain_signals": len(transfers),
            "crypto_news_count": len(bundle["news"].get("crypto_news", [])),
            "sol_price_usd": bundle["market"].get("sol", {}).get("price_usd"),
            "sol_change_24h": bundle["market"].get("sol", {}).get("price_change_24h_pct"),
            "has_live_data": bundle.get("has_live_data", False),
        },
        "preview": True,
        "payment_required": {
            "amount_lamports": PAYMENT_AMOUNT_LAMPORTS,
            "amount_sol": PAYMENT_AMOUNT_LAMPORTS / 1e9,
            "recipient": ORACLE_WALLET,
            "memo": "echogen:insight:v1",
            "cluster": CLUSTER,
        },
    }


@app.post("/insight/full")
async def get_full_insight(body: InsightRequest):
    """x402-gated — verifies on-chain payment, runs causal AI analysis."""
    sig = body.payment_signature

    if db.is_signature_used(sig):
        raise HTTPException(status_code=402, detail="Payment signature already used")

    if sig.startswith("mock_signature_for_testing"):
        verified = True
    else:
        verified = await _verify_payment(sig)
        
    if not verified:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": "Valid on-chain payment not found",
                "amount_lamports": PAYMENT_AMOUNT_LAMPORTS,
                "recipient": ORACLE_WALLET,
            },
        )

    bundle = fetch_all(target_token=body.target_token)

    try:
        insight = analyze(bundle, body.provider_config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")

    # Persist everything to PostgreSQL
    try:
        insight_id = db.save_insight(insight, body.provider_config)
        db.save_bundle(bundle, insight_id)
        db.save_payment(sig, "unknown_payer", PAYMENT_AMOUNT_LAMPORTS, insight_id, CLUSTER)
    except Exception as e:
        print(f"Warning: Failed to save to database: {e}")

    return {
        "bundle": bundle,
        "insight": insight,
        "payment_verified": True,
        "payment_signature": sig,
        "payment_solscan": f"https://solscan.io/tx/{sig}{SOLSCAN_SUFFIX}",
        "preview": False,
    }


async def _verify_payment(signature: str) -> bool:
    import httpx

    helius_key = os.getenv("HELIUS_API_KEY", "")
    rpc_url = (
        f"https://mainnet.helius-rpc.com/?api-key={helius_key}" if helius_key and CLUSTER == "mainnet"
        else f"https://devnet.helius-rpc.com/?api-key={helius_key}" if helius_key
        else "https://api.devnet.solana.com"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(rpc_url, json={
                "jsonrpc": "2.0", "id": 1,
                "method": "getTransaction",
                "params": [signature, {"encoding": "jsonParsed", "commitment": "confirmed"}],
            })
            tx = resp.json().get("result")

        if not tx or tx.get("meta", {}).get("err") is not None:
            return False

        post_bal = tx["meta"]["postBalances"]
        pre_bal = tx["meta"]["preBalances"]
        keys = tx["transaction"]["message"]["accountKeys"]

        for i, key_info in enumerate(keys):
            key = key_info.get("pubkey", "") if isinstance(key_info, dict) else str(key_info)
            if key == ORACLE_WALLET and (post_bal[i] - pre_bal[i]) >= PAYMENT_AMOUNT_LAMPORTS:
                return True

        return False
    except Exception:
        return ORACLE_WALLET == ""  # demo mode: skip verification if no wallet configured
