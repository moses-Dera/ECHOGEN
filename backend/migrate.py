
"""
EchoGen — Database Migration Script
Run this once to create all tables in PostgreSQL.
Safe to re-run: uses IF NOT EXISTS on all statements.

Usage:
    cd backend/
    python migrate.py
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
load_dotenv("../.env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/echogen")

MIGRATION_SQL = """
-- ─────────────────────────────────────────────────────────────
-- EchoGen PostgreSQL Schema
-- Mirrors prisma/schema.prisma for Python backend access
-- ─────────────────────────────────────────────────────────────

-- Enable gen_random_uuid() if not already available
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ── Insights (Core Intelligence Reports) ─────────────────────
CREATE TABLE IF NOT EXISTS insights (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- AI output
    headline        TEXT NOT NULL,
    causal_chain    TEXT NOT NULL,
    confidence      INTEGER NOT NULL DEFAULT 0,
    risk_level      TEXT NOT NULL DEFAULT 'MEDIUM',
    tags            TEXT[] DEFAULT '{}',
    corroborated_by TEXT[] DEFAULT '{}',

    -- Layer summaries
    summary_on_chain TEXT,
    summary_market   TEXT,
    summary_news     TEXT,

    -- AI provider metadata
    ai_provider     TEXT,
    ai_model        TEXT,

    -- On-chain oracle proof
    memo_signature  TEXT UNIQUE,
    memo_solscan    TEXT
);

-- ── Payments (x402 On-Chain Verification) ────────────────────
CREATE TABLE IF NOT EXISTS payments (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Solana transaction
    signature       TEXT UNIQUE NOT NULL,
    payer_wallet    TEXT NOT NULL,
    amount          BIGINT NOT NULL,
    cluster         TEXT NOT NULL DEFAULT 'devnet',
    solscan_url     TEXT NOT NULL,

    -- Verification
    verified        BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at     TIMESTAMPTZ,

    -- Link to insight
    insight_id      TEXT UNIQUE NOT NULL REFERENCES insights(id) ON DELETE CASCADE
);

-- ── Signal Bundles (Raw Sensor Snapshots) ────────────────────
CREATE TABLE IF NOT EXISTS signal_bundles (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Raw JSON from each layer
    on_chain_data   JSONB NOT NULL DEFAULT '{}',
    market_data     JSONB NOT NULL DEFAULT '{}',
    news_data       JSONB NOT NULL DEFAULT '{}',

    -- Metadata
    sources_used    TEXT[] DEFAULT '{}',
    has_live_data   BOOLEAN NOT NULL DEFAULT FALSE,

    -- Link to insight
    insight_id      TEXT UNIQUE NOT NULL REFERENCES insights(id) ON DELETE CASCADE
);

-- ── User Settings (Per-Wallet AI Preferences) ────────────────
CREATE TABLE IF NOT EXISTS user_settings (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    wallet_address  TEXT UNIQUE NOT NULL,

    -- AI config
    ai_provider     TEXT NOT NULL DEFAULT 'openai',
    ai_base_url     TEXT NOT NULL DEFAULT 'https://api.openai.com/v1',
    ai_model        TEXT NOT NULL DEFAULT 'gpt-4o-mini'
);

-- ── Indexes ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_insights_created_at ON insights(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_insights_risk_level ON insights(risk_level);
CREATE INDEX IF NOT EXISTS idx_payments_signature ON payments(signature);
CREATE INDEX IF NOT EXISTS idx_payments_payer ON payments(payer_wallet);
CREATE INDEX IF NOT EXISTS idx_bundles_insight ON signal_bundles(insight_id);
CREATE INDEX IF NOT EXISTS idx_settings_wallet ON user_settings(wallet_address);
"""


def migrate():
    print(f"Connecting to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(MIGRATION_SQL)
        conn.commit()
        print("✅ Migration complete — all tables created.")

        # Verify tables
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cur.fetchall()]
            print(f"   Tables: {', '.join(tables)}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
