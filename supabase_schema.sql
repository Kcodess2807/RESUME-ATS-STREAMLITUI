-- Supabase Schema for ATS Resume Scorer
-- This creates the analysis_history table for storing resume analysis results

-- Create the analysis_history table
CREATE TABLE IF NOT EXISTS analysis_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,  -- Can be UUID (authenticated) or session_xxx (anonymous)
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

-- Drop old policy if exists
DROP POLICY IF EXISTS "Allow all operations" ON analysis_history;

-- Create policy for authenticated users to access their own data
CREATE POLICY "Users can access their own history" ON analysis_history
    FOR ALL
    USING (
        -- Allow if user_id matches authenticated user's ID
        auth.uid()::text = user_id
        OR
        -- Allow if user_id is a session ID (for backwards compatibility)
        user_id LIKE 'session_%'
    )
    WITH CHECK (
        -- Allow insert/update if user_id matches authenticated user's ID
        auth.uid()::text = user_id
        OR
        -- Allow if user_id is a session ID (for backwards compatibility)
        user_id LIKE 'session_%'
    );

-- Note: With Google OAuth authentication enabled:
-- - Authenticated users: user_id will be their Supabase auth UUID
-- - Anonymous users: user_id will be "session_xxx" (session-based)
-- - History is tied to user accounts for authenticated users
-- - History is tied to browser sessions for anonymous users

