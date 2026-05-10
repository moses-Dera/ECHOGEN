"use client";

import { SensorSource, SignalBundle } from "../lib/types";
import { CheckCircle2, Clock, ExternalLink, Database, Globe, Zap, AlertCircle } from "lucide-react";

const LAYER_LABEL: Record<string, string> = {
  on_chain: "Layer 1 — Ground Truth",
  market: "Layer 2 — Market Momentum",
  news: "Layer 3 — Causal Catalyst",
};

const STATUS_STYLE: Record<string, string> = {
  live: "bg-emerald-500/10 text-emerald-500",
  fallback: "bg-amber-500/10 text-amber-500",
  error: "bg-red-500/10 text-red-500",
  unknown: "bg-border-low text-muted",
};

// Honest upgrade notes shown when a sensor is on fallback
const UPGRADE_NOTES: Record<string, { reason: string; action: string; href: string }> = {
  "sensors.helius": {
    reason: "Helius API key not configured.",
    action: "Get free key at helius.dev → RPCs → Show API Keys",
    href: "https://helius.dev",
  },
  "sensors.news": {
    reason: "CryptoPanic requires a paid plan ($50/week). Currently using NewsAPI for macro news.",
    action: "Upgrade at cryptopanic.com/api/plans when ready",
    href: "https://cryptopanic.com/api/plans",
  },
};

interface Props {
  sources: SensorSource[];
  bundle: SignalBundle;
}

export function SourcesPanel({ sources, bundle }: Props) {
  const liveCount = sources.filter((s) => s.status === "live").length;

  return (
    <div className="space-y-4">

      {/* Overall status bar */}
      <div className="rounded-xl border border-border-low bg-cream p-3 flex items-center justify-between">
        <p className="text-xs font-mono text-muted">
          <span className="text-foreground font-semibold">{liveCount}/{sources.length}</span> sensors live
        </p>
        <div className="flex items-center gap-3">
          {sources.map((s) => (
            <span key={s.module} className="flex items-center gap-1 text-[10px] font-mono text-muted">
              <span className={`h-1.5 w-1.5 rounded-full ${s.status === "live" ? "bg-emerald-500" : "bg-amber-500"}`} />
              {s.label.split(" ")[0]}
            </span>
          ))}
        </div>
      </div>

      {sources.map((s) => {
        const layerData = bundle[s.layer as keyof SignalBundle] as Record<string, unknown> | undefined;
        const isLive = s.status === "live";
        const upgradeNote = !isLive ? UPGRADE_NOTES[s.module] : null;

        return (
          <div key={s.module} className="rounded-xl border border-border-low bg-card p-4 space-y-3">

            {/* Header */}
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-0.5">
                <p className="text-xs text-muted font-mono uppercase tracking-widest">
                  {LAYER_LABEL[s.layer] ?? s.layer}
                </p>
                <p className="text-sm font-semibold">{s.label}</p>
              </div>
              <span className={`rounded-full px-2 py-0.5 text-xs font-mono shrink-0 ${STATUS_STYLE[s.status] ?? STATUS_STYLE.unknown}`}>
                {isLive ? "● live" : "○ demo data"}
              </span>
            </div>

            {/* Honest upgrade note when not live */}
            {upgradeNote && (
              <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2 space-y-1">
                <p className="text-xs text-amber-600 dark:text-amber-400">{upgradeNote.reason}</p>
                <a
                  href={upgradeNote.href}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-foreground underline underline-offset-2 hover:opacity-70 transition flex items-center gap-1"
                >
                  {upgradeNote.action} <ExternalLink size={10} />
                </a>
              </div>
            )}

            {/* Layer-specific live data preview */}
            {s.layer === "on_chain" && bundle.on_chain && (
              <div className="font-mono text-xs text-muted space-y-1">
                <p>{bundle.on_chain.whale_transfers.length} whale transfer(s) detected</p>
                {bundle.on_chain.whale_transfers.slice(0, 2).map((t, i) => (
                  <p key={i} className="truncate">
                    <span className="text-foreground">{t.amount_sol?.toLocaleString() ?? "?"} SOL</span>
                    {" "}→ {t.to_label ?? t.to_address.slice(0, 12) + "…"}
                    {" "}
                    <span className={t.direction === "exchange_inflow" ? "text-red-400" : "text-emerald-400"}>
                      [{t.direction.replace("_", " ")}]
                    </span>
                  </p>
                ))}
              </div>
            )}

            {s.layer === "market" && bundle.market?.sol && (
              <div className="font-mono text-xs text-muted grid grid-cols-2 gap-x-4 gap-y-1">
                <p>price <span className="text-foreground">${bundle.market.sol.price_usd?.toLocaleString()}</span></p>
                <p>24h <span className={bundle.market.sol.price_change_24h_pct < 0 ? "text-red-400" : "text-emerald-400"}>
                  {bundle.market.sol.price_change_24h_pct?.toFixed(2)}%
                </span></p>
                <p>vol <span className="text-foreground">${(bundle.market.sol.volume_24h_usd / 1e9).toFixed(1)}B</span></p>
                <p>mcap <span className="text-foreground">${(bundle.market.sol.market_cap_usd / 1e9).toFixed(0)}B</span></p>
              </div>
            )}

            {s.layer === "news" && bundle.news && (
              <div className="space-y-1.5">
                {[...bundle.news.crypto_news, ...(bundle.news.macro_news ?? [])].slice(0, 3).map((n, i) => {
                  const sentiment = (n as any).sentiment;
                  return (
                    <a
                      key={i}
                      href={n.url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-start gap-2 group"
                    >
                      <span className={`mt-0.5 shrink-0 rounded px-1 py-0.5 text-[10px] font-mono ${
                        sentiment === "positive" ? "bg-emerald-500/10 text-emerald-500"
                        : sentiment === "negative" ? "bg-red-500/10 text-red-500"
                        : "bg-border-low text-muted"
                      }`}>
                        {(n as any).category ?? (sentiment || "news")}
                      </span>
                      <span className="text-xs text-muted group-hover:text-foreground transition line-clamp-2">
                        {n.title}
                      </span>
                    </a>
                  );
                })}
              </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between pt-1 border-t border-border-low">
              {s.url ? (
                <a href={s.url} target="_blank" rel="noreferrer"
                  className="text-xs text-muted hover:text-foreground transition underline underline-offset-2 flex items-center gap-1">
                  {s.url.replace("https://", "")} <ExternalLink size={10} />
                </a>
              ) : <span />}
              <span className="text-[10px] text-muted font-mono">
                {isLive
                  ? `fetched ${new Date(s.fetched_at).toLocaleTimeString()}`
                  : "using demo data"}
              </span>
            </div>
          </div>
        );
      })}

      {/* Roadmap note for judges */}
      <div className="rounded-xl border border-border-low bg-cream p-4 space-y-1">
        <p className="text-xs font-semibold text-foreground">Data Source Roadmap</p>
        <ul className="text-xs text-muted space-y-2 pt-2 list-none">
          <li className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-emerald-500" />
            <span>CoinGecko — live, no key required</span>
          </li>
          <li className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-emerald-500" />
            <span>NewsAPI — live, macro + Solana news</span>
          </li>
          <li className="flex items-center gap-2 opacity-70">
            <Clock size={14} className="text-amber-500" />
            <span>Helius — pending API key (free, helius.dev)</span>
          </li>
          <li className="flex items-center gap-2 opacity-70">
            <Clock size={14} className="text-amber-500" />
            <span>CryptoPanic — pending paid plan ($50/week)</span>
          </li>
          <li className="flex items-center gap-2 opacity-70">
            <Clock size={14} className="text-amber-500" />
            <span>Birdeye — pending API key for DEX depth</span>
          </li>
        </ul>
        <p className="text-[10px] text-muted pt-1">
          Architecture supports plug-in sensors — each source is a single file drop in <code className="bg-card px-1 rounded">backend/sensors/</code>
        </p>
      </div>
    </div>
  );
}
