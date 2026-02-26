-- Mise à jour du schéma pour supporter TMDB
ALTER TABLE video_analyses 
ADD COLUMN IF NOT EXISTS tmdb_id INTEGER,
ADD COLUMN IF NOT EXISTS tmdb_data JSONB,
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Index pour la recherche rapide
CREATE INDEX IF NOT EXISTS idx_video_analyses_tmdb_id ON video_analyses(tmdb_id);
CREATE INDEX IF NOT EXISTS idx_video_analyses_video_path_trgm ON video_analyses USING gin(video_path gin_trgm_ops);

-- Mise à jour du trigger pour last_updated
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_update_last_updated ON video_analyses;
CREATE TRIGGER tr_update_last_updated
    BEFORE UPDATE ON video_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated();

-- Vue pour les suggestions de recherche
CREATE OR REPLACE VIEW v_show_suggestions AS
SELECT 
    va.id,
    va.video_path as title,
    va.pacing_score,
    va.tmdb_id,
    va.tmdb_data->>'poster_path' as poster_path,
    va.tmdb_data->>'backdrop_path' as backdrop_path,
    va.tmdb_data->>'first_air_date' as first_air_date
FROM video_analyses va
WHERE va.tmdb_id IS NOT NULL;