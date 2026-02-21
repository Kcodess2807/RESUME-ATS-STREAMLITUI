-- ATS Resume Scorer - Supabase Database Schema
-- Run this in your Supabase SQL Editor

-- Create analysis_history table
CREATE TABLE IF NOT EXISTS analysis_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    overall_score FLOAT NOT NULL,
    formatting_score FLOAT,
    keywords_score FLOAT,
    content_score FLOAT,
    skill_validation_score FLOAT,
    ats_compatibility_score FLOAT,
    jd_match_percentage FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON analysis_history(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE analysis_history ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to read their own data
CREATE POLICY "Users can view their own analysis history"
    ON analysis_history
    FOR SELECT
    USING (true);  -- Allow all reads for now, can be restricted later

-- Create policy to allow users to insert their own data
CREATE POLICY "Users can insert their own analysis history"
    ON analysis_history
    FOR INSERT
    WITH CHECK (true);  -- Allow all inserts for now

-- Create policy to allow users to delete their own data
CREATE POLICY "Users can delete their own analysis history"
    ON analysis_history
    FOR DELETE
    USING (true);  -- Allow all deletes for now

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_analysis_history_updated_at
    BEFORE UPDATE ON analysis_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON analysis_history TO authenticated;
GRANT ALL ON analysis_history TO anon;
