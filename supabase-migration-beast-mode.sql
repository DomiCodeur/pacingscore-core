-- Mollo Beast Mode: Ajout des colonnes manquantes
-- À exécuter dans Supabase → SQL Editor → Nouvelle requête

-- 1. Ajouter colonnes analysis_tasks (certaines existent déjà)
ALTER TABLE analysis_tasks ADD COLUMN IF NOT EXISTS error_message TEXT;
ALTER TABLE analysis_tasks ADD COLUMN IF NOT EXISTS media_type TEXT DEFAULT 'tv';
ALTER TABLE analysis_tasks ADD COLUMN IF NOT EXISTS manual_url TEXT;
ALTER TABLE analysis_tasks ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 1;

-- 2. Ajouter colonnes mollo_scores (certaines existent déjà)
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS motion_intensity FLOAT;
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS source TEXT;
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS video_type TEXT;

-- 3. Index pour performance
CREATE INDEX IF NOT EXISTS idx_analysis_tasks_status ON analysis_tasks(status);
