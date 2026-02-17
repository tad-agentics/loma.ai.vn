-- Loma database schema — Supabase PostgreSQL
-- Run this in Supabase SQL Editor to initialize the database.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Users table
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    auth_provider TEXT NOT NULL DEFAULT 'google',
    subscription_tier TEXT NOT NULL DEFAULT 'free'
        CHECK (subscription_tier IN ('free', 'payg', 'pro')),
    payg_balance INTEGER NOT NULL DEFAULT 0,
    rewrites_today INTEGER NOT NULL DEFAULT 0,
    last_rewrite_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- ============================================================
-- Rewrites table
-- ============================================================
CREATE TABLE IF NOT EXISTS rewrites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    detected_intent TEXT,
    intent_confidence REAL,
    routing_tier TEXT CHECK (routing_tier IN ('rules', 'haiku', 'sonnet')),
    output_language TEXT,
    platform TEXT,
    tone TEXT,
    language_mix JSONB,
    scores JSONB,
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rewrites_user ON rewrites (user_id);
CREATE INDEX IF NOT EXISTS idx_rewrites_created ON rewrites (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rewrites_intent ON rewrites (detected_intent);

-- ============================================================
-- Events table (analytics)
-- ============================================================
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_name TEXT NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_user ON events (user_id);
CREATE INDEX IF NOT EXISTS idx_events_name ON events (event_name);
CREATE INDEX IF NOT EXISTS idx_events_created ON events (created_at DESC);

-- ============================================================
-- Payments table (PayOS audit trail)
-- ============================================================
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    order_code BIGINT UNIQUE,
    amount INTEGER NOT NULL,
    product TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    provider TEXT NOT NULL DEFAULT 'payos',
    provider_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_user ON payments (user_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments (order_code);

-- ============================================================
-- Row Level Security (RLS)
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE rewrites ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- Users can read/update their own row
CREATE POLICY users_self_read ON users FOR SELECT
    USING (auth.uid() = id);
CREATE POLICY users_self_update ON users FOR UPDATE
    USING (auth.uid() = id);

-- Users can read their own rewrites
CREATE POLICY rewrites_self_read ON rewrites FOR SELECT
    USING (auth.uid() = user_id);

-- Users can read their own payments
CREATE POLICY payments_self_read ON payments FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can do everything (backend uses service key)
CREATE POLICY service_all_users ON users FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY service_all_rewrites ON rewrites FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY service_all_events ON events FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY service_all_payments ON payments FOR ALL
    USING (auth.role() = 'service_role');
