/**
 * Publishes an insight as a Solana Memo transaction.
 * Uses raw instruction — Memo program treats all instruction data as UTF-8.
 * Only depends on @solana/kit (already in the project).
 */
import {
  pipe,
  createTransactionMessage,
  setTransactionMessageFeePayerSigner,
  setTransactionMessageLifetimeUsingBlockhash,
  appendTransactionMessageInstruction,
  signAndSendTransactionMessageWithSigners,
  createSolanaRpc,
  address,
  getBase58Codec,
  type TransactionSigner,
} from "@solana/kit";

const MEMO_PROGRAM_ID = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr";

const CLUSTER = process.env.NEXT_PUBLIC_SOLANA_CLUSTER ?? "devnet";
const RPC_URL =
  CLUSTER === "mainnet"
    ? "https://api.mainnet-beta.solana.com"
    : "https://api.devnet.solana.com";
const SOLSCAN_SUFFIX = CLUSTER === "mainnet" ? "" : "?cluster=devnet";

export async function publishInsightMemo(
  insight: { headline: string; confidence: number; risk_level: string },
  signer: TransactionSigner,
): Promise<{ signature: string; solscanUrl: string }> {
  const rpc = createSolanaRpc(RPC_URL);

  const memoText = JSON.stringify({
    app: "echogen",
    v: 1,
    headline: insight.headline,
    confidence: insight.confidence,
    risk: insight.risk_level,
    ts: Date.now(),
  });

  const memoInstruction = {
    programAddress: address(MEMO_PROGRAM_ID),
    accounts: [] as [],
    data: new TextEncoder().encode(memoText),
  };

  const { value: latestBlockhash } = await rpc.getLatestBlockhash().send();

  const message = pipe(
    createTransactionMessage({ version: 0 }),
    (m) => setTransactionMessageFeePayerSigner(signer, m),
    (m) => setTransactionMessageLifetimeUsingBlockhash(latestBlockhash, m),
    (m) => appendTransactionMessageInstruction(memoInstruction, m),
  );

  const sig = await signAndSendTransactionMessageWithSigners(message);
  const sigStr = getBase58Codec().decode(sig);

  return {
    signature: sigStr,
    solscanUrl: `https://solscan.io/tx/${sigStr}${SOLSCAN_SUFFIX}`,
  };
}
