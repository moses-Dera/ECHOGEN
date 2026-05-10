"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { BookOpen, Settings, Search, CheckCircle, Wallet, Globe, ArrowRight } from "lucide-react";
import { useWalletConnection } from "@solana/react-hooks";
import {
  fetchPreview,
  fetchFullInsight,
  ProviderConfig,
  PreviewResponse,
  FullInsightResponse,
} from "./lib/x402";
import { SettingsModal } from "./components/settings-modal";
import { OutputTabs } from "./components/output-tabs";

const DEFAULT_CONFIG: ProviderConfig = {
  base_url: "https://api.openai.com/v1",
  api_key: "",
  model: "gpt-4o-mini",
};

type Phase =
  | "idle"
  | "loading-preview"
  | "preview"
  | "paying"
  | "loading-insight"
  | "insight"
  | "error";

/** Build a raw System Program transfer instruction (no @solana-program/system needed). */
function buildTransferInstruction(
  fromAddress: string,
  toAddress: string,
  lamports: bigint,
) {
  // System Program transfer: instruction index 2, little-endian u64 amount
  const data = new Uint8Array(12);
  new DataView(data.buffer).setUint32(0, 2, true); // instruction index
  new DataView(data.buffer).setBigUint64(4, lamports, true); // amount

  return {
    programAddress: "11111111111111111111111111111111" as `${string}`,
    accounts: [
      {
        address: fromAddress as `${string}`,
        role: 3 as const, // WRITABLE_SIGNER
      },
      {
        address: toAddress as `${string}`,
        role: 1 as const, // WRITABLE
      },
    ],
    data,
  };
}

export default function Home() {
  const { connectors, connect, disconnect, wallet, status } =
    useWalletConnection();
  const [phase, setPhase] = useState<Phase>("idle");
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [insight, setInsight] = useState<FullInsightResponse | null>(null);
  const [error, setError] = useState("");
  const [config, setConfig] = useState<ProviderConfig>(DEFAULT_CONFIG);
  const [showSettings, setShowSettings] = useState(false);
  const [memoSolscan, setMemoSolscan] = useState("");
  const [targetToken, setTargetToken] = useState("SOL");

  const walletAddress = wallet?.account.address.toString();

  const loadPreview = useCallback(async () => {
    setPhase("loading-preview");
    setError("");
    try {
      const data = await fetchPreview(targetToken);
      setPreview(data);
      setPhase("preview");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load signal");
      setPhase("error");
    }
  }, [targetToken]);

  useEffect(() => {
    loadPreview();
  }, [loadPreview]);

  // Load config from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("echogen_config");
    if (saved) {
      try {
        setConfig(JSON.parse(saved));
      } catch (e) {
        // ignore parse error
      }
    }
  }, []);

  function handleConfigChange(newConfig: ProviderConfig) {
    setConfig(newConfig);
    localStorage.setItem("echogen_config", JSON.stringify(newConfig));
  }

  async function handlePay() {
    if (!wallet || !preview) return;
    if (!config.api_key) {
      setShowSettings(true);
      return;
    }

    setPhase("paying");
    setError("");

    try {
      const {
        pipe,
        createTransactionMessage,
        setTransactionMessageFeePayerSigner,
        setTransactionMessageLifetimeUsingBlockhash,
        appendTransactionMessageInstruction,
        signAndSendTransactionMessageWithSigners,
        createSolanaRpc,
        getBase58Codec,
      } = await import("@solana/kit");

      const cluster = process.env.NEXT_PUBLIC_SOLANA_CLUSTER ?? "devnet";
      const rpcUrl =
        cluster === "mainnet"
          ? "https://api.mainnet-beta.solana.com"
          : "https://api.devnet.solana.com";

      const rpc = createSolanaRpc(rpcUrl);
      const { value: latestBlockhash } = await rpc.getLatestBlockhash().send();

      // wallet from @solana/react-hooks is a TransactionSendingSigner-compatible object
      const signer = wallet as unknown as Parameters<
        typeof setTransactionMessageFeePayerSigner
      >[0];

      const recipient = preview.payment_required.recipient;
      const amount = BigInt(preview.payment_required.amount_lamports);

      const transferIx = buildTransferInstruction(
        wallet.account.address.toString(),
        recipient,
        amount,
      );

      // const message = pipe(
      //   createTransactionMessage({ version: 0 }),
      //   (m) => setTransactionMessageFeePayerSigner(signer, m),
      //   (m) =>
      //     setTransactionMessageLifetimeUsingBlockhash(latestBlockhash, m),
      //   (m) => appendTransactionMessageInstruction(transferIx as never, m),
      // );
      // 
      // const sig = await signAndSendTransactionMessageWithSigners(message);
      // const sigStr = getBase58Codec().decode(sig);

      // Bypass payment for testing
      const sigStr = "mock_signature_for_testing_" + Date.now();

      setPhase("loading-insight");

      const full = await fetchFullInsight(sigStr, config, targetToken);
      setInsight(full);

      // Publish insight to chain as memo (non-fatal)
      try {
        const { publishInsightMemo } = await import("./lib/publishMemo");
        const memo = await publishInsightMemo(
          full.insight,
          signer as import("@solana/kit").TransactionSigner,
        );
        setMemoSolscan(memo.solscanUrl);
      } catch {
        // non-fatal
      }

      setPhase("insight");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Transaction failed");
      setPhase("preview");
    }
  }

  return (
    <div className="relative min-h-screen bg-bg1 text-foreground">
      {showSettings && (
        <SettingsModal
          config={config}
          onChange={handleConfigChange}
          onClose={() => setShowSettings(false)}
        />
      )}

      {/* Top Navigation */}
      <div className="absolute top-6 right-6 z-50 flex gap-4">
        <Link
          href="/docs"
          className="rounded-full border border-white/10 bg-white/5 backdrop-blur-md px-6 py-2.5 text-sm font-medium text-accent hover:bg-white/10 hover:border-accent/50 transition-all cursor-pointer shadow-[0_0_15px_rgba(0,240,255,0.1)] flex items-center gap-2"
        >
          <BookOpen size={16} /> Read Whitepaper
        </Link>
      </div>

      <main className="mx-auto max-w-4xl px-6 py-20 space-y-10 relative z-10">
        <header className="space-y-4 text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-accent font-mono animate-pulse">
            Solana Intelligence Oracle
          </p>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-200 to-accent">
            EchoGen
          </h1>
          <p className="text-lg text-gray-300 max-w-3xl mx-auto leading-relaxed">
            The Autonomous Reasoning Layer for Solana. Transforming raw signals into plain-language causal intelligence, published on-chain via x402 with ElevenLabs AI audio briefings.
          </p>
        </header>

        {/* Search & Configuration Bar */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Token Search Bar */}
          <div className="relative w-full md:w-96 group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-accent">
              <Search size={18} />
            </div>
            <input
              type="text"
              suppressHydrationWarning
              placeholder="Search token (e.g. WIF, BONK, SOL)..."
              value={targetToken}
              onChange={(e) => setTargetToken(e.target.value.toUpperCase())}
              onKeyDown={(e) => {
                if (e.key === "Enter") loadPreview();
              }}
              className="w-full bg-white/5 border border-white/10 rounded-full py-3 pl-12 pr-6 text-sm font-mono focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-all placeholder:text-muted"
            />
            <button 
              onClick={loadPreview}
              className="absolute right-2 top-1.5 bottom-1.5 px-4 rounded-full bg-accent text-black text-xs font-bold hover:brightness-110 transition cursor-pointer"
            >
              RESOLVE
            </button>
          </div>

          <div className="flex items-center gap-4">
            {status !== "connected" ? (
              <div className="flex gap-2">
                {connectors.length > 0 ? (
                  connectors.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => connect(c.id)}
                      className="rounded-full border border-white/10 bg-white/5 backdrop-blur-md px-6 py-2.5 text-sm font-medium hover:bg-white/10 hover:border-accent/50 transition-all cursor-pointer"
                    >
                      Connect {c.name}
                    </button>
                  ))
                ) : (
                  <a
                    href="https://phantom.app/ul/browse/https%3A%2F%2Fechogen-rosy.vercel.app%2F?ref=https%3A%2F%2Fechogen-rosy.vercel.app%2F"
                    className="rounded-full border border-accent/30 bg-accent/10 backdrop-blur-md px-6 py-2.5 text-sm font-medium hover:bg-accent/20 hover:border-accent/50 transition-all cursor-pointer flex items-center gap-2 text-accent"
                  >
                    <Wallet size={16} /> Open in Phantom
                  </a>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-2 text-sm font-mono shadow-[0_0_15px_rgba(16,185,129,0.15)]">
                  {walletAddress?.slice(0, 6)}…{walletAddress?.slice(-4)}
                </span>
                <button
                  onClick={() => disconnect()}
                  className="text-xs text-muted hover:text-white transition cursor-pointer uppercase tracking-widest"
                >
                  Disconnect
                </button>
              </div>
            )}
            <button
              onClick={() => setShowSettings(true)}
              className="rounded-full border border-white/10 bg-white/5 backdrop-blur-md px-6 py-2.5 text-sm font-medium hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer flex items-center gap-2"
            >
              <Settings size={18} className={config.api_key ? "text-emerald-400" : ""} />
              {config.api_key && <CheckCircle size={12} className="text-emerald-400" />}
            </button>
          </div>
        </div>

        {/* Signal Preview Card */}
        {(phase === "preview" ||
          phase === "paying" ||
          phase === "loading-insight" ||
          phase === "insight") &&
          preview && (
            <section className="glass-card rounded-3xl p-8 space-y-6 animate-float">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                  <p className="text-sm uppercase tracking-widest text-accent font-mono">
                    Live Signal Detected
                  </p>
                </div>
                <span className="rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-500 px-3 py-1 text-xs font-mono shadow-[0_0_10px_rgba(245,158,11,0.2)]">
                  {preview.signal.source === "fallback" ? "DEMO MODE" : "LIVE"}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bento-box space-y-2">
                  <p className="text-xs text-muted uppercase tracking-widest">Signal Type</p>
                  <p className="text-lg font-semibold text-white">{String(preview.signal.type ?? "—")}</p>
                </div>
                <div className="bento-box space-y-2">
                  <p className="text-xs text-muted uppercase tracking-widest">Volume Detected</p>
                  <p className="text-2xl font-bold text-accent">{Number(preview.signal.amount_sol ?? 0).toLocaleString()} <span className="text-sm text-muted">SOL</span></p>
                </div>
                <div className="bento-box space-y-2">
                  <p className="text-xs text-muted uppercase tracking-widest">Source (From)</p>
                  <p className="text-sm font-mono text-indigo-300">{String(preview.signal.from ?? "—").slice(0, 20)}…</p>
                </div>
                <div className="bento-box space-y-2">
                  <p className="text-xs text-muted uppercase tracking-widest">Destination (To)</p>
                  <p className="text-sm font-mono text-purple-300">{String(preview.signal.to ?? "—").slice(0, 20)}…</p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-xs text-muted font-mono">Detected at: {String(preview.signal.timestamp ?? "—")}</p>
              </div>

              {phase !== "insight" && (
                <div className="border-t border-white/10 pt-6 space-y-4">
                  <p className="text-sm text-center text-gray-300">
                    Unlock deep AI causal reasoning for <span className="text-accent font-bold">{preview.payment_required.amount_sol} SOL</span>
                  </p>
                  <button
                    onClick={handlePay}
                    disabled={
                      status !== "connected" ||
                      phase === "paying" ||
                      phase === "loading-insight"
                    }
                    className="w-full glass-button rounded-2xl py-4 text-base tracking-wide shadow-xl disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                  >
                    {phase === "paying" && "Awaiting Signature..."}
                    {phase === "loading-insight" &&
                      "Verifying Payment & Synthesizing Insight..."}
                    {phase === "preview" &&
                      (status === "connected"
                        ? "Pay & Unlock Intelligence →"
                        : "Connect Wallet to Proceed")}
                  </button>
                  {error && (
                    <p className="text-xs text-red-400 font-mono text-center bg-red-400/10 py-2 rounded-lg">{error}</p>
                  )}
                </div>
              )}
            </section>
          )}

        {/* Loading skeleton */}
        {phase === "loading-preview" && (
          <div className="rounded-2xl border border-border-low bg-card p-6 animate-pulse space-y-3">
            <div className="h-3 w-24 rounded bg-border-low" />
            <div className="h-3 w-full rounded bg-border-low" />
            <div className="h-3 w-3/4 rounded bg-border-low" />
          </div>
        )}

        {/* Full Insight Card — replaced by OutputTabs */}
        {phase === "insight" && insight && (
          <OutputTabs
            insight={insight}
            memoSolscan={memoSolscan}
            onReset={() => {
              setPhase("preview");
              setInsight(null);
              setMemoSolscan("");
              loadPreview();
            }}
          />
        )}

        {phase === "error" && (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6 space-y-2">
            <p className="text-sm font-semibold text-red-500">Error</p>
            <p className="text-sm text-muted font-mono">{error}</p>
            <button
              onClick={loadPreview}
              className="text-xs text-foreground underline cursor-pointer"
            >
              Retry
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
