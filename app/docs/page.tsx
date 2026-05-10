import Link from "next/link";
import { ArrowLeft, Zap, Shield, Database, LayoutGrid, Globe, Rocket } from "lucide-react";

export default function DocsPage() {
  return (
    <div className="relative min-h-screen bg-bg1 text-foreground">
      <main className="mx-auto max-w-4xl px-6 py-20 space-y-16 relative z-10">
        
        {/* Navigation */}
        <nav>
          <Link 
            href="/" 
            className="text-sm font-mono text-muted hover:text-white transition-colors flex items-center gap-2 group"
          >
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> 
            Back to Oracle Terminal
          </Link>
        </nav>

        {/* Header */}
        <header className="space-y-6 text-center md:text-left">
          <p className="text-xs uppercase tracking-[0.3em] text-accent font-mono">
            Autonomous Reasoning Layer
          </p>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-200 to-accent leading-tight">
            EchoGen
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl leading-relaxed">
            Bridging the gap between raw blockchain data and human-readable causal intelligence for the Solana ecosystem.
          </p>
        </header>

        {/* The Problem / Solution */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="glass-card rounded-3xl p-8 space-y-4">
            <h2 className="text-xl font-semibold text-red-400">The Problem: Information Fragmentation</h2>
            <p className="text-gray-300 leading-relaxed text-sm">
              Blockchain data is public, but its meaning is fragmented. When a signal occurs on-chain, the context is buried across news feeds, social media, and liquidity maps. There is a massive &quot;meaning gap&quot; between a transaction hash and a causal explanation.
            </p>
          </div>
          <div className="glass-card rounded-3xl p-8 space-y-4 border-accent/30 shadow-[0_0_30px_rgba(0,240,255,0.1)]">
            <h2 className="text-xl font-semibold text-accent">The Solution: Autonomous Reasoning</h2>
            <p className="text-gray-300 leading-relaxed text-sm">
              EchoGen acts as the autonomous reasoning layer. It ingests data from dozens of sources, synthesizes it using advanced LLMs, and generates plain-language explanations. It is an economic actor that gates high-value intelligence via the <span className="text-white font-mono">x402</span> protocol.
            </p>
          </div>
        </section>

        {/* Strategic Vision */}
        <section className="space-y-8">
          <div className="space-y-2 text-center md:text-left">
            <h2 className="text-3xl font-bold tracking-tight">Strategic Achievement Goals</h2>
            <p className="text-sm text-muted">What we are building for the Solana ecosystem.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-card p-8 rounded-3xl border border-white/5 space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <Shield size={24} />
              </div>
              <h3 className="text-lg font-bold">Establish "Proof of Thought"</h3>
              <p className="text-sm text-muted leading-relaxed">
                By anchoring every AI reasoning step to the Solana Memo Program, we create a verifiable, auditable record of the Oracle's logic—preventing hallucinations and ensuring accountability.
              </p>
            </div>
            <div className="glass-card p-8 rounded-3xl border border-white/5 space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-accent/10 flex items-center justify-center text-accent">
                <Zap size={24} />
              </div>
              <h3 className="text-lg font-bold">Prove the x402 Economy</h3>
              <p className="text-sm text-muted leading-relaxed">
                We demonstrate that autonomous agents can be self-sustaining. By gating high-value intelligence with the x402 protocol, the agent earns its own revenue to cover compute costs.
              </p>
            </div>
            <div className="glass-card p-8 rounded-3xl border border-white/5 space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                <Globe size={24} />
              </div>
              <h3 className="text-lg font-bold">Synthesize Causal Truth</h3>
              <p className="text-sm text-muted leading-relaxed">
                Transform thousands of fragmented on-chain signals into a single, high-fidelity explanation delivered in plain language and ElevenLabs AI Audio.
              </p>
            </div>
            <div className="glass-card p-8 rounded-3xl border border-white/5 space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-purple-500/10 flex items-center justify-center text-purple-400">
                <Rocket size={24} />
              </div>
              <h3 className="text-lg font-bold">Scale the Reasoning Stack</h3>
              <p className="text-sm text-muted leading-relaxed">
                Provide a decentralized, plug-and-play architecture where specialized sensors can be added in minutes to monitor any part of the Solana ecosystem.
              </p>
            </div>
          </div>
        </section>

        {/* Autonomous Unit Economics */}
        <section className="space-y-8">
          <div className="space-y-2 text-center md:text-left">
            <h2 className="text-3xl font-bold tracking-tight">Autonomous Unit Economics</h2>
            <p className="text-sm text-muted">Proving the "Intelligence Margin" of self-sustaining agents.</p>
          </div>
          <div className="glass-card rounded-3xl overflow-hidden border border-white/5 bg-white/5">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white/5">
                  <th className="px-6 py-4 text-xs uppercase tracking-widest text-muted font-mono">Component</th>
                  <th className="px-6 py-4 text-xs uppercase tracking-widest text-muted font-mono text-right">Cost (Est.)</th>
                  <th className="px-6 py-4 text-xs uppercase tracking-widest text-muted font-mono text-right">Revenue (Est.)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono text-sm">
                <tr>
                  <td className="px-6 py-4 text-gray-300">LLM Reasoning (Gemini Flash)</td>
                  <td className="px-6 py-4 text-red-400 text-right">-$0.01</td>
                  <td className="px-6 py-4 text-right">—</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-gray-300">ElevenLabs AI Audio</td>
                  <td className="px-6 py-4 text-red-400 text-right">-$0.05</td>
                  <td className="px-6 py-4 text-right">—</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-gray-300">Data Ingestion (Helius/Birdeye)</td>
                  <td className="px-6 py-4 text-red-400 text-right">-$0.01</td>
                  <td className="px-6 py-4 text-right">—</td>
                </tr>
                <tr className="bg-accent/5">
                  <td className="px-6 py-4 font-bold text-accent">x402 Per-Insight Payment</td>
                  <td className="px-6 py-4 text-right">—</td>
                  <td className="px-6 py-4 font-bold text-emerald-400 text-right">+$0.15</td>
                </tr>
                <tr className="bg-white/5">
                  <td className="px-6 py-6 text-lg font-bold text-white">Net Agent Profit</td>
                  <td className="px-6 py-6 text-right">—</td>
                  <td className="px-6 py-6 text-xl font-bold text-accent text-right">~$0.08</td>
                </tr>
              </tbody>
            </table>
            <div className="p-8 bg-accent/5 border-t border-white/5">
              <p className="text-sm font-semibold text-accent uppercase tracking-widest mb-2">Strategic Summary</p>
              <p className="text-gray-300 leading-relaxed italic">
                This high intelligence margin allows <span className="text-white font-bold">EchoGen</span> to fund its own expansion, data ingestion, and development without external capital. By closing the loop between reasoning and monetization, EchoGen transforms from a simple analysis tool into a fully <span className="text-accent font-bold">autonomous business entity</span> on the Solana ledger.
              </p>
            </div>
          </div>
        </section>

        {/* Architecture Layers */}
        <section className="space-y-8">
          <div className="space-y-2 text-center md:text-left">
            <h2 className="text-3xl font-bold tracking-tight">The 3-Layer Intelligence Stack</h2>
            <p className="text-sm text-muted">A multi-agent approach to synthesizing truth from chaos.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bento-box bg-white/5 space-y-4 p-8 border-l-4 border-indigo-500">
              <h3 className="font-semibold text-xl">L1: Ground Truth</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Raw on-chain state monitoring via <span className="text-white font-mono">Helius RPC</span>. Tracking whale transfers, smart-money flows, and system program deployments.
              </p>
            </div>

            <div className="bento-box bg-white/5 space-y-4 p-8 border-l-4 border-emerald-500">
              <h3 className="font-semibold text-xl">L2: Market Momentum</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                DEX analytics and security profiles via <span className="text-white font-mono">Birdeye & DexScreener</span>. Analyzing volume spikes and liquidity depth across SPL tokens.
              </p>
            </div>

            <div className="bento-box bg-white/5 space-y-4 p-8 border-l-4 border-accent">
              <h3 className="font-semibold text-xl text-accent">L3: Causal Catalyst</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Global context via <span className="text-white font-mono">NewsAPI, NewsData.io, NewsAPI.ai, & RSS</span>. Identifying real-world events driving the blockchain activity.
              </p>
            </div>
          </div>
        </section>

        {/* Sensor Registry */}
        <section className="space-y-6">
          <div className="space-y-2">
            <h2 className="text-2xl font-bold tracking-tight">Data Sensor Registry</h2>
            <p className="text-sm text-muted">Currently active autonomous data ingestors.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {[
              { name: "Helius On-Chain", icon: <Database size={12} /> },
              { name: "Birdeye V3", icon: <Globe size={12} /> },
              { name: "DexScreener", icon: <LayoutGrid size={12} /> },
              { name: "Binance Global", icon: <Globe size={12} /> },
              { name: "CoinMarketCap", icon: <Zap size={12} /> },
              { name: "NewsAPI", icon: <Globe size={12} /> },
              { name: "NewsData.io", icon: <Globe size={12} /> },
              { name: "NewsAPI.ai", icon: <Zap size={12} /> },
              { name: "ChainGPT AI News", icon: <Rocket size={12} /> },
              { name: "Decrypt RSS", icon: <Database size={12} /> },
              { name: "CoinTelegraph RSS", icon: <Database size={12} /> },
              { name: "CoinDesk RSS", icon: <Database size={12} /> }
            ].map(s => (
              <span key={s.name} className="rounded-full bg-white/5 border border-white/10 px-4 py-2 text-xs font-mono text-gray-300 flex items-center gap-2">
                {s.icon} {s.name}
              </span>
            ))}
          </div>
        </section>

        {/* Project Roadmap */}
        <section className="space-y-10">
          <div className="space-y-2">
            <h2 className="text-3xl font-bold tracking-tight">Project Roadmap</h2>
            <p className="text-sm text-muted">From Hackathon MVP to Decentralized Intelligence Layer.</p>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {[
              { phase: "Phase 1: Hackathon MVP", goal: "Single-agent reasoning, x402 payment gating, ElevenLabs audio narration briefings, and verified on-chain memo publishing.", active: true },
              { phase: "Phase 2: Multi-Agent Coordination", goal: "Integration of LangGraph to allow specialized agents to collaborate on complex cross-domain events.", active: false },
              { phase: "Phase 3: Semantic Memory", goal: "Implementation of vector databases to create a long-term library of historical Solana ecosystem events.", active: false },
              { phase: "Phase 4: Relationship Visualization", goal: "Interactive graph visualization of how on-chain movements correlate with global market catalysts.", active: false },
              { phase: "Phase 5: Multi-Ecosystem", goal: "Expansion beyond Solana to monitor Ethereum, Bitcoin, and Avalanche signal propagation.", active: false },
            ].map((p, i) => (
              <div key={i} className={`flex items-center gap-6 p-6 rounded-2xl border transition-all ${p.active ? "bg-accent/5 border-accent shadow-[0_0_20px_rgba(0,240,255,0.05)]" : "bg-white/5 border-white/10 opacity-50"}`}>
                <div className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center font-mono text-sm ${p.active ? "bg-accent text-black" : "bg-white/10 text-white"}`}>
                  0{i + 1}
                </div>
                <div>
                  <h4 className={`font-semibold ${p.active ? "text-accent" : "text-white"}`}>{p.phase}</h4>
                  <p className="text-xs text-gray-400 mt-1">{p.goal}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Call to Action */}
        <section className="text-center pt-8 pb-20">
          <Link 
            href="/"
            className="glass-button inline-flex rounded-full px-10 py-5 font-bold text-xl shadow-[0_0_50px_rgba(79,70,229,0.4)]"
          >
            Launch Oracle Terminal
          </Link>
        </section>

      </main>
    </div>
  );
}
