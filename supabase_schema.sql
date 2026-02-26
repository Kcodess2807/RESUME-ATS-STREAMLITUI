-- Supabase Schema for ATS Resume Scorer
-- This creates the analysis_history table for storing resume analysis results

-- Create the analysis_history table
CREATE TABLE IF NOT EXISTS analysis_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    overall_score INTEGER NOT NULL,
    formatting_score INTEGER NOT NULL,
    keywords_score INTEGER NOT NULL,
    content_score INTEGER NOT NULL,
    skill_validation_score INTEGER NOT NULL,
    ats_compatibility_score INTEGER NOT NULL,
    jd_match_percentage INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON analysis_history(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (since we're not using Supabase auth)
-- Users are identified by session_id, not authenticated users
CREATE POLICY "Allow all operations" ON analysis_history
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Note: Since authentication is removed, we use session-based user_ids
-- Each session gets a unique ID like "session_a1b2c3d4"
-- This means history is tied to browser sessions, not user accounts
