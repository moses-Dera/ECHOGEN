-- CreateTable
CREATE TABLE "insights" (
    "id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "headline" TEXT NOT NULL,
    "causal_chain" TEXT NOT NULL,
    "confidence" INTEGER NOT NULL,
    "risk_level" TEXT NOT NULL,
    "tags" TEXT[],
    "corroborated_by" TEXT[],
    "summary_on_chain" TEXT,
    "summary_market" TEXT,
    "summary_news" TEXT,
    "ai_provider" TEXT,
    "ai_model" TEXT,
    "memo_signature" TEXT,
    "memo_solscan" TEXT,

    CONSTRAINT "insights_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "payments" (
    "id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "signature" TEXT NOT NULL,
    "payer_wallet" TEXT NOT NULL,
    "amount" BIGINT NOT NULL,
    "cluster" TEXT NOT NULL DEFAULT 'devnet',
    "solscan_url" TEXT NOT NULL,
    "verified" BOOLEAN NOT NULL DEFAULT false,
    "verified_at" TIMESTAMP(3),
    "insight_id" TEXT NOT NULL,

    CONSTRAINT "payments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "signal_bundles" (
    "id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "on_chain_data" JSONB NOT NULL,
    "market_data" JSONB NOT NULL,
    "news_data" JSONB NOT NULL,
    "sources_used" TEXT[],
    "has_live_data" BOOLEAN NOT NULL DEFAULT false,
    "insight_id" TEXT NOT NULL,

    CONSTRAINT "signal_bundles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_settings" (
    "id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "wallet_address" TEXT NOT NULL,
    "ai_provider" TEXT NOT NULL DEFAULT 'openai',
    "ai_base_url" TEXT NOT NULL DEFAULT 'https://api.openai.com/v1',
    "ai_model" TEXT NOT NULL DEFAULT 'gpt-4o-mini',

    CONSTRAINT "user_settings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "insights_memo_signature_key" ON "insights"("memo_signature");

-- CreateIndex
CREATE UNIQUE INDEX "payments_signature_key" ON "payments"("signature");

-- CreateIndex
CREATE UNIQUE INDEX "payments_insight_id_key" ON "payments"("insight_id");

-- CreateIndex
CREATE UNIQUE INDEX "signal_bundles_insight_id_key" ON "signal_bundles"("insight_id");

-- CreateIndex
CREATE UNIQUE INDEX "user_settings_wallet_address_key" ON "user_settings"("wallet_address");

-- AddForeignKey
ALTER TABLE "payments" ADD CONSTRAINT "payments_insight_id_fkey" FOREIGN KEY ("insight_id") REFERENCES "insights"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "signal_bundles" ADD CONSTRAINT "signal_bundles_insight_id_fkey" FOREIGN KEY ("insight_id") REFERENCES "insights"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
