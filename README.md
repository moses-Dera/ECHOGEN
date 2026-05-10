# EchoGen: Autonomous Reasoning Layer for Solana

**EchoGen** is an autonomous intelligence system designed to solve the problem of **Information Fragmentation** in the Solana ecosystem. While blockchain data is public and abundant, its meaning is often obscured by noise. EchoGen transforms raw on-chain state and market signals into plain-language, causal explanations, published as a verifiable Intelligence Oracle.

---

## The Vision: Solving the Meaning Gap
In Web3, data exists, but context is missing. When a large wallet moves funds or a token price spikes, the "What" is visible on Solscan, but the "Why" is buried in fragmented news feeds, social media, and complex liquidity maps. 

EchoGen acts as a **Multi-Agent Reasoning Layer** that bridges this gap. It doesn't just show you data; it tells you what it means, why it happened, and what the likely next causal step will be.

## Strategic Mission & Achievement Goals

1.  **Establish "Proof of Thought":** By anchoring every AI reasoning step to the **Solana Memo Program**, we create a verifiable, auditable record of the Oracle's logic—preventing hallucinations and ensuring accountability.
2.  **Prove the x402 Economy:** We demonstrate that autonomous agents can be self-sustaining. By gating high-value intelligence with the **x402 protocol**, the agent earns its own revenue to cover compute and RPC costs.
3.  **Synthesize Causal Truth:** Transform thousands of fragmented on-chain signals into a single, high-fidelity explanation delivered in plain language and **ElevenLabs AI Audio**.
4.  **Scale the Reasoning Stack:** Provide a decentralized, plug-and-play architecture where specialized sensors can be added in minutes to monitor any part of the Solana ecosystem.

---

## How It Works: The 3-Layer Intelligence Stack

EchoGen utilizes a sophisticated, multi-layered ingestion engine to synthesize truth:

1. **Layer 1: On-Chain Ground Truth (Helius)**
   - Monitors raw Solana system program transfers, whale movements, and smart-money flows.
2. **Layer 2: Market Momentum (Birdeye V3)**
   - Analyzes real-time DEX volume, liquidity depth, and token security profiles (detecting honeypots and rug-pull risks).
3. **Layer 3: Causal Catalyst (Global News & Sentiment)**
   - Ingests data from **NewsAPI**, **NewsData.io**, **Event Registry (NewsAPI.ai)**, and various **RSS feeds** (CoinDesk, Decrypt, etc.) to identify the real-world event triggering the on-chain movement.

---

## Key Solana Integrations

### 1. The x402 API Payment Gateway
Intelligence has value. EchoGen implements the **x402 protocol** (extending HTTP 402). To unlock an autonomous reasoning report, users must provide a valid on-chain payment signature, verified by the backend against the Solana ledger.

### 2. Verifiable Memo Records
To ensure accountability and prevent AI hallucinations, every generated insight is hashed and published to the **Solana Memo Program**. This creates a permanent, auditable trail of the Oracle's reasoning that anyone can verify on Solscan.

### 3. Dynamic Token Routing
Using Birdeye's V3 Search, EchoGen can resolve any ticker symbol (e.g., `$SOL`, `$WIF`, `$BONK`) to its specific mint address, allowing the system to scale its intelligence across the entire Solana ecosystem.

---

## Project Roadmap

EchoGen is currently in the **Hackathon MVP Phase**. The long-term vision includes:

- **Phase 1 (Hackathon MVP):** Single-agent reasoning, multi-layer data ingestion, **x402 protocol payment gating**, **ElevenLabs AI audio briefings**, and verifiable **Solana Memo** publishing.
- **Phase 2:** Multi-Agent coordination via LangGraph for cross-domain relationship detection.
- **Phase 3:** Long-term semantic memory using vector databases (historical event library).
- **Phase 4:** Relationship graph visualization of the entire Solana ecosystem.
- **Phase 5:** Multi-ecosystem expansion (Ethereum, Bitcoin, Avalanche connectors).

---

## Technical Stack

- **Frontend:** Next.js 15, Tailwind CSS (Glassmorphic Web3 UI), `@solana/web3.js`.
- **Backend:** Python FastAPI, Prisma ORM, PostgreSQL.
- **AI Engine:** Provider-agnostic (OpenAI, Gemini 1.5, Claude, Groq).
- **Audio:** ElevenLabs authoritative narration briefings.
- **Data:** Helius, Birdeye, NewsAPI, NewsData.io, NewsAPI.ai, RSS.
