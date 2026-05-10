export interface ProviderConfig {
  base_url: string;
  api_key: string;
  model: string;
}

export interface SensorSource {
  module: string;
  layer: string;
  label: string;
  url: string | null;
  requires_key: boolean;
  key_env_var: string | null;
  status: "live" | "fallback" | "error" | "unknown";
  fetched_at: string;
}

export interface SignalBundle {
  on_chain?: {
    source: string;
    whale_transfers: Array<{
      signature: string;
      amount_sol: number | null;
      from_address: string;
      from_label?: string | null;
      to_address: string;
      to_label?: string | null;
      direction: string;
      token: string;
      timestamp: string;
    }>;
    token_metadata: Record<string, { name: string; symbol: string }>;
  };
  market?: {
    source: string;
    sol: {
      price_usd: number;
      market_cap_usd: number;
      volume_24h_usd: number;
      price_change_24h_pct: number;
      price_change_1h_pct?: number;
    };
    dex?: {
      liquidity_usd: number;
      volume_24h_usd: number;
      buy_24h: number;
      sell_24h: number;
    } | null;
  };
  news?: {
    source: string;
    crypto_news: Array<{
      title: string;
      url: string;
      sentiment: "positive" | "negative" | "neutral";
      importance: "high" | "medium" | "low";
      votes_bullish?: number;
      votes_bearish?: number;
      published_at: string;
      source: string;
    }>;
    macro_news: Array<{
      title: string;
      url: string;
      source: string;
      published_at: string;
    }>;
  };
  sources: SensorSource[];
  fetched_at: string;
  has_live_data: boolean;
}

export interface Insight {
  headline: string;
  causal_chain: string;
  confidence: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  tags: string[];
  layer_summary: {
    on_chain: string;
    market: string;
    news: string;
  };
  corroborated_by: string[];
}

export interface PreviewResponse {
  signal: Record<string, unknown>;
  bundle_summary: {
    on_chain_signals: number;
    crypto_news_count: number;
    sol_price_usd: number | null;
    sol_change_24h: number | null;
    has_live_data: boolean;
  };
  payment_required: {
    amount_lamports: number;
    amount_sol: number;
    recipient: string;
    memo: string;
    cluster: string;
  };
}

export interface FullInsightResponse {
  bundle: SignalBundle;
  insight: Insight;
  payment_verified: boolean;
  payment_signature: string;
  payment_solscan: string;
}
