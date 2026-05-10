export type { ProviderConfig, PreviewResponse, FullInsightResponse, SignalBundle, Insight, SensorSource } from "./types";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export async function fetchPreview(targetToken?: string) {
  const url = new URL(`${BACKEND}/insight`);
  if (targetToken) url.searchParams.set("target_token", targetToken);
  
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch signal preview");
  return res.json();
}

export async function fetchFullInsight(
  paymentSignature: string,
  providerConfig: import("./types").ProviderConfig,
  targetToken: string = "SOL",
): Promise<import("./types").FullInsightResponse> {
  const res = await fetch(`${BACKEND}/insight/full`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      payment_signature: paymentSignature,
      provider_config: providerConfig,
      target_token: targetToken,
    }),
  });

  if (res.status === 402) {
    const err = await res.json();
    throw new Error(`Payment required: ${JSON.stringify(err.detail)}`);
  }
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "Unknown error");
  }
  return res.json();
}

export async function fetchSources(): Promise<import("./types").SensorSource[]> {
  const res = await fetch(`${BACKEND}/sources`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.sources ?? [];
}

export async function narrateInsight(text: string): Promise<string> {
  const res = await fetch(`${BACKEND}/narrate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Narration unavailable");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}
