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
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON users (stripe_customer_id);

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
-- Row Level Security (RLS)
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE rewrites ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Users can read/update their own row
CREATE POLICY users_self_read ON users FOR SELECT
    USING (auth.uid() = id);
CREATE POLICY users_self_update ON users FOR UPDATE
    USING (auth.uid() = id);

-- Users can read their own rewrites
CREATE POLICY rewrites_self_read ON rewrites FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can do everything (backend uses service key)
CREATE POLICY service_all_users ON users FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY service_all_rewrites ON rewrites FOR ALL
    USING (auth.role() = 'service_role');
CREATE POLICY service_all_events ON events FOR ALL
    USING (auth.role() = 'service_role');
