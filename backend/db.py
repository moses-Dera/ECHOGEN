"""
EchoGen — Database layer (PostgreSQL via psycopg2).
Shares the same DB as the Prisma schema on the Next.js side.

Tables:
  insights       — AI causal intelligence reports
  payments       — x402 on-chain payment records
  signal_bundles — raw sensor data snapshots
  user_settings  — per-wallet AI provider preferences
"""
import os
import json
from datetime import datetime, timezone
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
load_dotenv("../.env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/echogen")


@contextmanager
def get_conn():
    """Context-managed database connection."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Insights ──────────────────────────────────────────────────

def save_insight(insight: dict, provider_config: dict | None = None) -> str:
    """
    Persist a causal intelligence report.
    Returns the generated insight ID.
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO insights (
                    id, created_at, headline, causal_chain, confidence,
                    risk_level, tags, corroborated_by,
                    summary_on_chain, summary_market, summary_news,
                    ai_provider, ai_model
                ) VALUES (
                    gen_random_uuid()::text, NOW(), %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                ) RETURNING id
            """, (
                insight.get("headline", ""),
                insight.get("causal_chain", ""),
                insight.get("confidence", 0),
                insight.get("risk_level", "MEDIUM"),
                insight.get("tags", []),
                insight.get("corroborated_by", []),
                insight.get("layer_summary", {}).get("on_chain"),
                insight.get("layer_summary", {}).get("market"),
                insight.get("layer_summary", {}).get("news"),
                provider_config.get("base_url", "").split("//")[-1].split("/")[0] if provider_config else None,
                provider_config.get("model") if provider_config else None,
            ))
            return cur.fetchone()[0]


def update_insight_memo(insight_id: str, memo_signature: str, memo_solscan: str):
    """Attach the on-chain memo proof to an existing insight."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE insights
                SET memo_signature = %s, memo_solscan = %s
                WHERE id = %s
            """, (memo_signature, memo_solscan, insight_id))


def get_recent_insights(limit: int = 20) -> list[dict]:
    """Fetch the most recent insights for the feed."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT i.*, p.signature as payment_signature, p.solscan_url as payment_solscan
                FROM insights i
                LEFT JOIN payments p ON p.insight_id = i.id
                ORDER BY i.created_at DESC
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]


# ── Payments ──────────────────────────────────────────────────

def save_payment(signature: str, payer_wallet: str, amount: int,
                 insight_id: str, cluster: str = "devnet") -> str:
    """
    Record a verified x402 payment.
    Returns the payment ID.
    """
    solscan_suffix = "" if cluster == "mainnet" else "?cluster=devnet"
    solscan_url = f"https://solscan.io/tx/{signature}{solscan_suffix}"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO payments (
                    id, created_at, signature, payer_wallet, amount,
                    cluster, solscan_url, verified, verified_at, insight_id
                ) VALUES (
                    gen_random_uuid()::text, NOW(), %s, %s, %s,
                    %s, %s, TRUE, NOW(), %s
                ) RETURNING id
            """, (signature, payer_wallet, amount, cluster, solscan_url, insight_id))
            return cur.fetchone()[0]


def is_signature_used(signature: str) -> bool:
    """Check if a payment signature has already been redeemed."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM payments WHERE signature = %s", (signature,))
            return cur.fetchone() is not None


# ── Signal Bundles ────────────────────────────────────────────

def save_bundle(bundle: dict, insight_id: str) -> str:
    """Persist a raw signal bundle snapshot linked to an insight."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            sources_used = [s.get("name", s.get("module", "unknown"))
                           for s in bundle.get("sources", [])]
            cur.execute("""
                INSERT INTO signal_bundles (
                    id, created_at, on_chain_data, market_data, news_data,
                    sources_used, has_live_data, insight_id
                ) VALUES (
                    gen_random_uuid()::text, NOW(),
                    %s::jsonb, %s::jsonb, %s::jsonb,
                    %s, %s, %s
                ) RETURNING id
            """, (
                json.dumps(bundle.get("on_chain", {})),
                json.dumps(bundle.get("market", {})),
                json.dumps(bundle.get("news", {})),
                sources_used,
                bundle.get("has_live_data", False),
                insight_id,
            ))
            return cur.fetchone()[0]


# ── User Settings ─────────────────────────────────────────────

def get_user_settings(wallet_address: str) -> dict | None:
    """Fetch AI preferences for a wallet."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM user_settings WHERE wallet_address = %s",
                (wallet_address,)
            )
            row = cur.fetchone()
            return dict(row) if row else None


def upsert_user_settings(wallet_address: str, provider: str, base_url: str, model: str):
    """Create or update AI preferences for a wallet."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_settings (id, created_at, updated_at, wallet_address, ai_provider, ai_base_url, ai_model)
                VALUES (gen_random_uuid()::text, NOW(), NOW(), %s, %s, %s, %s)
                ON CONFLICT (wallet_address)
                DO UPDATE SET ai_provider = %s, ai_base_url = %s, ai_model = %s, updated_at = NOW()
            """, (wallet_address, provider, base_url, model, provider, base_url, model))
