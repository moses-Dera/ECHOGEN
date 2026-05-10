"use client";

import { useState } from "react";
import { ProviderConfig } from "../lib/x402";
import { X, Save, Cpu } from "lucide-react";

const PRESETS = [
  { label: "Gemini 1.5 Flash", base_url: "https://generativelanguage.googleapis.com/v1beta/openai", model: "gemini-1.5-flash" },
  { label: "OpenAI GPT-4o", base_url: "https://api.openai.com/v1", model: "gpt-4o" },
  { label: "OpenAI GPT-4o Mini", base_url: "https://api.openai.com/v1", model: "gpt-4o-mini" },
  { label: "Anthropic Claude Haiku", base_url: "https://api.anthropic.com/v1", model: "claude-3-5-haiku-20241022" },
  { label: "Groq Llama 3.3 70B", base_url: "https://api.groq.com/openai/v1", model: "llama-3.3-70b-versatile" },
  { label: "Custom", base_url: "", model: "" },
];

interface Props {
  config: ProviderConfig;
  onChange: (c: ProviderConfig) => void;
  onClose: () => void;
}

export function SettingsModal({ config, onChange, onClose }: Props) {
  const [local, setLocal] = useState<ProviderConfig>(config);
  const [preset, setPreset] = useState(PRESETS[0].label);

  function applyPreset(label: string) {
    const p = PRESETS.find((x) => x.label === label)!;
    setPreset(label);
    if (p.base_url) setLocal((c) => ({ ...c, base_url: p.base_url, model: p.model }));
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl glass-card p-6 shadow-[0_0_50px_rgba(0,0,0,0.5)] space-y-4">
        <div className="flex items-center justify-between">
          <p className="font-semibold text-lg flex items-center gap-2">
            <Cpu size={20} className="text-accent" /> Intelligence Settings
          </p>
          <button onClick={onClose} className="text-muted hover:text-white transition cursor-pointer">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-1">
          <label className="text-xs text-muted uppercase tracking-wide">AI Provider</label>
          <select
            value={preset}
            onChange={(e) => applyPreset(e.target.value)}
            className="w-full rounded-lg border border-border-low bg-cream px-3 py-2 text-sm font-mono"
          >
            {PRESETS.map((p) => <option key={p.label}>{p.label}</option>)}
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-xs text-muted uppercase tracking-wide">API Base URL</label>
          <input
            value={local.base_url}
            onChange={(e) => setLocal((c) => ({ ...c, base_url: e.target.value }))}
            placeholder="https://api.openai.com/v1"
            className="w-full rounded-lg border border-border-low bg-cream px-3 py-2 text-sm font-mono"
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs text-muted uppercase tracking-wide">Model</label>
          <input
            value={local.model}
            onChange={(e) => setLocal((c) => ({ ...c, model: e.target.value }))}
            placeholder="gpt-4o-mini"
            className="w-full rounded-lg border border-border-low bg-cream px-3 py-2 text-sm font-mono"
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs text-muted uppercase tracking-wide">API Key</label>
          <input
            type="password"
            value={local.api_key}
            onChange={(e) => setLocal((c) => ({ ...c, api_key: e.target.value }))}
            placeholder="sk-..."
            className="w-full rounded-lg border border-border-low bg-cream px-3 py-2 text-sm font-mono"
          />
        </div>

        <p className="text-xs text-muted">
          Your key is stored in browser memory only — never sent to our servers. It goes directly to your chosen provider.
        </p>

        <button
          onClick={() => { onChange(local); onClose(); }}
          className="w-full rounded-xl bg-foreground text-background py-3 text-sm font-semibold hover:opacity-90 transition cursor-pointer flex items-center justify-center gap-2"
        >
          <Save size={16} /> Save Intelligence Profile
        </button>
      </div>
    </div>
  );
}
