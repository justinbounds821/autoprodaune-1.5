-- services/api/database/video_phase9.sql
-- Phase 9 database schema for video AI features

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Video jobs table (if not exists)
CREATE TABLE IF NOT EXISTS video_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    status text NOT NULL DEFAULT 'queued',
    script text,
    video_url text,
    thumb_url text,
    error text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    completed_at timestamptz
);

-- Video insights table
CREATE TABLE IF NOT EXISTS video_insights (
    job_id uuid PRIMARY KEY REFERENCES video_jobs(id) ON DELETE CASCADE,
    tags text[] DEFAULT '{}',
    scene_cuts float[] DEFAULT '{}',
    vector_embedding vector(384),
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Video captions table
CREATE TABLE IF NOT EXISTS video_captions (
    job_id uuid PRIMARY KEY REFERENCES video_jobs(id) ON DELETE CASCADE,
    lang text NOT NULL DEFAULT 'ro',
    srt_url text,
    ass_url text,
    text_content text,
    created_at timestamptz DEFAULT now()
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS video_insights_embedding_idx 
ON video_insights 
USING ivfflat (vector_embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for tag-based queries
CREATE INDEX IF NOT EXISTS video_insights_tags_idx 
ON video_insights 
USING gin (tags);

-- Function to search similar videos
CREATE OR REPLACE FUNCTION search_similar_videos(
    q vector(384),
    min_score float DEFAULT 0.7,
    k int DEFAULT 10
)
RETURNS TABLE(
    job_id uuid,
    score float,
    tags text[],
    thumb_url text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vi.job_id,
        1 - (vi.vector_embedding <=> q) AS score,
        vi.tags,
        vj.thumb_url
    FROM video_insights vi
    JOIN video_jobs vj ON vj.id = vi.job_id
    WHERE vi.vector_embedding IS NOT NULL
        AND (1 - (vi.vector_embedding <=> q)) >= min_score
    ORDER BY vi.vector_embedding <=> q
    LIMIT k;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_video_jobs_updated_at ON video_jobs;
CREATE TRIGGER update_video_jobs_updated_at
BEFORE UPDATE ON video_jobs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_video_insights_updated_at ON video_insights;
CREATE TRIGGER update_video_insights_updated_at
BEFORE UPDATE ON video_insights
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE video_insights IS 'AI-generated insights for video jobs including tags, scene cuts, and embeddings';
COMMENT ON TABLE video_captions IS 'Auto-generated captions from Whisper or other services';
COMMENT ON FUNCTION search_similar_videos IS 'Semantic search for similar videos using cosine similarity';
