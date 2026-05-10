"use client";

import { useState, useRef } from "react";
import { FullInsightResponse } from "../lib/types";
import { SourcesPanel } from "./sources-panel";
import { narrateInsight } from "../lib/x402";
import { Volume2, RotateCcw, ExternalLink, FileText, Code, Headphones, ArrowRight, CheckCircle2 } from "lucide-react";

const RISK_COLOR: Record<string, string> = {
  LOW: "text-emerald-500",
  MEDIUM: "text-amber-500",
  HIGH: "text-red-500",
};

const CORROBORATION_COLOR: Record<string, string> = {
  "Layer 1": "bg-blue-500/10 text-blue-400",
  "Layer 2": "bg-purple-500/10 text-purple-400",
  "Layer 3": "bg-orange-500/10 text-orange-400",
};

type Tab = "report" | "sources" | "raw" | "audio";

interface Props {
  insight: FullInsightResponse;
  memoSolscan: string;
  onReset: () => void;
}

export function OutputTabs({ insight, memoSolscan, onReset }: Props) {
  const [tab, setTab] = useState<Tab>("report");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioLoading, setAudioLoading] = useState(false);
  const [audioError, setAudioError] = useState("");
  const audioRef = useRef<HTMLAudioElement>(null);

  async function handleNarrate() {
    setAudioLoading(true);
    setAudioError("");
    try {
      const url = await narrateInsight(insight.insight.causal_chain);
      setAudioUrl(url);
      setTab("audio");
      setTimeout(() => audioRef.current?.play(), 100);
    } catch (e: unknown) {
      setAudioError(e instanceof Error ? e.message : "Narration failed");
    } finally {
      setAudioLoading(false);
    }
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: "report", label: "Report" },
    { id: "sources", label: `Sources (${insight.bundle.sources?.length ?? 0})` },
    { id: "raw", label: "Raw JSON" },
    { id: "audio", label: "Audio" },
  ];

  return (
    <section className="rounded-2xl border border-border-low bg-card overflow-hidden">
      {/* Tab bar */}
      <div className="flex border-b border-border-low">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-3 text-xs font-mono uppercase tracking-widest transition cursor-pointer ${
              tab === t.id
                ? "text-foreground border-b-2 border-foreground -mb-px"
                : "text-muted hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="p-6">
        {/* ── Report tab ── */}
        {tab === "report" && (
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <p className="text-xs uppercase tracking-widest text-muted font-mono">
                Causal Intelligence Report
              </p>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-mono font-semibold ${RISK_COLOR[insight.insight.risk_level] ?? "text-muted"}`}>
                  {insight.insight.risk_level} RISK
                </span>
                <span className="rounded-full bg-emerald-500/10 text-emerald-500 px-2 py-0.5 text-xs font-mono">
                  {insight.insight.confidence}% confidence
                </span>
              </div>
            </div>

            <p className="text-lg font-semibold leading-snug">{insight.insight.headline}</p>

            {/* Causal chain */}
            <div className="rounded-2xl bg-white/5 border border-white/5 p-6 space-y-4">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                {/* Confidence Gauge */}
                <div className="relative w-32 h-20 shrink-0">
                  <svg className="w-full h-full" viewBox="0 0 100 60">
                    <path
                      d="M 10 50 A 40 40 0 0 1 90 50"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="8"
                      className="text-white/10"
                    />
                    <path
                      d="M 10 50 A 40 40 0 0 1 90 50"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="8"
                      strokeDasharray="125.6"
                      strokeDashoffset={125.6 * (1 - insight.insight.confidence / 100)}
                      className="text-accent transition-all duration-1000 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
                    <span className="text-xl font-bold text-white">{insight.insight.confidence}%</span>
                    <span className="text-[10px] text-muted uppercase tracking-tighter">Confidence</span>
                  </div>
                </div>

                <div className="space-y-1 flex-1">
                  <p className="text-xs text-muted font-mono uppercase tracking-widest mb-2">Causal Chain</p>
                  <p className="text-sm leading-relaxed text-gray-200">{insight.insight.causal_chain}</p>
                </div>
              </div>
            </div>

            {/* Market Pulse / Sparkline */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               <div className="glass-card rounded-2xl p-5 border-l-4 border-accent space-y-3">
                  <div className="flex justify-between items-center">
                    <p className="text-[10px] uppercase tracking-widest text-muted">Price Action (24h)</p>
                    <span className={`text-xs font-mono ${(insight.bundle.market?.sol?.price_change_24h_pct ?? 0) >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                      {(insight.bundle.market?.sol?.price_change_24h_pct ?? 0).toFixed(2)}%
                    </span>
                  </div>
                  <div className="h-12 w-full flex items-end gap-1 px-1">
                    {[40, 70, 45, 90, 65, 80, 50, 95, 85, 100].map((h, i) => (
                      <div 
                        key={i} 
                        className="flex-1 bg-accent/20 rounded-t-sm animate-pulse" 
                        style={{ height: `${h}%`, animationDelay: `${i * 100}ms` }} 
                      />
                    ))}
                  </div>
                  <p className="text-lg font-bold text-white">
                    ${(insight.bundle.market?.sol?.price_usd ?? 0).toLocaleString()} <span className="text-[10px] text-muted font-normal uppercase ml-1">USD</span>
                  </p>
               </div>

               <div className="glass-card rounded-2xl p-5 border-l-4 border-indigo-500 space-y-3">
                  <p className="text-[10px] uppercase tracking-widest text-muted">Signal Magnitude</p>
                  <div className="flex items-center gap-4">
                    <div className="text-3xl font-bold text-white">{(insight.bundle.on_chain?.whale_transfers?.length ?? 0)}</div>
                    <div className="text-xs text-muted leading-tight">
                      Prominent signals detected across <br/> 3 reasoning layers.
                    </div>
                  </div>
                  <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-indigo-500 h-full w-[75%] shadow-[0_0_10px_rgba(99,102,241,0.5)]" />
                  </div>
               </div>
            </div>

            {/* Layer summaries */}
            {insight.insight.layer_summary && (
              <div className="space-y-2">
                <p className="text-xs text-muted font-mono uppercase tracking-widest">Layer Breakdown</p>
                {Object.entries(insight.insight.layer_summary).map(([layer, summary]) => (
                  <div key={layer} className="flex gap-3 text-sm">
                    <span className={`shrink-0 rounded px-2 py-0.5 text-xs font-mono self-start mt-0.5 ${
                      CORROBORATION_COLOR[`Layer ${layer === "on_chain" ? 1 : layer === "market" ? 2 : 3}`] ?? "bg-border-low text-muted"
                    }`}>
                      {layer === "on_chain" ? "L1" : layer === "market" ? "L2" : "L3"}
                    </span>
                    <p className="text-muted">{summary}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Corroboration + tags */}
            <div className="flex flex-wrap gap-2">
              {insight.insight.corroborated_by?.map((l) => (
                <span key={l} className={`rounded-full px-3 py-1 text-xs font-mono flex items-center gap-1 ${CORROBORATION_COLOR[l] ?? "bg-border-low text-muted"}`}>
                  <CheckCircle2 size={12} /> {l}
                </span>
              ))}
              {insight.insight.tags.map((tag) => (
                <span key={tag} className="rounded-full border border-border-low bg-cream px-3 py-1 text-xs font-mono">
                  #{tag}
                </span>
              ))}
            </div>

            {/* On-chain proof */}
            <div className="border-t border-border-low pt-4 space-y-2">
              <p className="text-xs uppercase tracking-widest text-muted font-mono">On-Chain Proof</p>
              <a href={insight.payment_solscan} target="_blank" rel="noreferrer"
                className="flex items-center gap-2 text-sm text-foreground underline underline-offset-2 hover:opacity-70 transition group">
                <span className="font-mono text-xs bg-cream px-2 py-1 rounded">x402</span>
                Payment verified <ArrowRight size={12} className="group-hover:translate-x-0.5 transition-transform" /> Solscan <ExternalLink size={12} />
              </a>
              {memoSolscan && (
                <a href={memoSolscan} target="_blank" rel="noreferrer"
                  className="flex items-center gap-2 text-sm text-foreground underline underline-offset-2 hover:opacity-70 transition group">
                  <span className="font-mono text-xs bg-cream px-2 py-1 rounded">MEMO</span>
                  Intelligence published on-chain <ArrowRight size={12} className="group-hover:translate-x-0.5 transition-transform" /> Solscan <ExternalLink size={12} />
                </a>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4 pt-1">
              <button
                onClick={handleNarrate}
                disabled={audioLoading}
                className="flex items-center gap-2 rounded-lg border border-border-low bg-card px-4 py-2 text-sm font-medium hover:-translate-y-0.5 hover:shadow-sm transition disabled:opacity-40 cursor-pointer group"
              >
                {audioLoading ? "Generating audio…" : (
                  <>
                    <Volume2 size={16} className="text-accent group-hover:scale-110 transition-transform" /> 
                    Narrate with ElevenLabs
                  </>
                )}
              </button>
              <button onClick={onReset} className="text-xs text-muted hover:text-white transition cursor-pointer uppercase tracking-widest flex items-center gap-2">
                <RotateCcw size={12} /> Analyze New Asset
              </button>
            </div>
            {audioError && <p className="text-xs text-red-500 font-mono">{audioError}</p>}
          </div>
        )}

        {/* ── Sources tab ── */}
        {tab === "sources" && (
          <SourcesPanel sources={insight.bundle.sources ?? []} bundle={insight.bundle} />
        )}

        {/* ── Raw JSON tab ── */}
        {tab === "raw" && (
          <div className="space-y-3">
            <p className="text-xs text-muted font-mono uppercase tracking-widest">Full Signal Bundle</p>
            <pre className="text-xs font-mono text-muted bg-cream rounded-xl p-4 overflow-auto max-h-[500px] leading-relaxed">
              {JSON.stringify(insight.bundle, null, 2)}
            </pre>
          </div>
        )}

        {/* ── Audio tab ── */}
        {tab === "audio" && (
          <div className="space-y-4">
            <p className="text-xs text-muted font-mono uppercase tracking-widest">ElevenLabs Narration</p>
            {audioUrl ? (
              <div className="space-y-3">
                <audio ref={audioRef} controls src={audioUrl} className="w-full" />
                <p className="text-xs text-muted font-mono">
                  Voice: SolaVision Analyst (Daniel) — powered by ElevenLabs
                </p>
                <p className="text-sm text-muted italic leading-relaxed">
                  "{insight.insight.causal_chain}"
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-sm text-muted">
                  Generate an authoritative audio narration of this intelligence report using ElevenLabs.
                </p>
                <button
                  onClick={handleNarrate}
                  disabled={audioLoading}
                  className="rounded-xl bg-foreground text-background px-6 py-2.5 text-sm font-semibold hover:opacity-90 transition disabled:opacity-40 cursor-pointer flex items-center gap-2"
                >
                  {audioLoading ? "Generating…" : (
                    <>
                      Generate Narration <ArrowRight size={16} />
                    </>
                  )}
                </button>
                {!process.env.NEXT_PUBLIC_BACKEND_URL && (
                  <p className="text-xs text-amber-500 font-mono">
                    Requires ELEVENLABS_API_KEY in backend .env
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
