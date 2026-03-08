-- Mollo Beast Mode: Préparation de la base pour 1000+ titres
-- À exécuter dans Supabase → SQL Editor → Nouvelle requête

-- 1. Assurez-vous que media_type existe
ALTER TABLE metadata_estimations ADD COLUMN IF NOT EXISTS media_type TEXT DEFAULT 'tv';
ALTER TABLE analysis_tasks ADD COLUMN IF NOT EXISTS media_type TEXT DEFAULT 'tv';

-- 2. Ajouter error_message aux tâches (pour tracking des échecs)
ALTER TABLE analysis_tasks ADD COLUMN IF NOT EXISTS error_message TEXT;

-- 3. Ajouter les colonnes de précision aux scores (certaines existent peut-être déjà)
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS motion_intensity FLOAT;
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS source_url TEXT;  -- utiliser video_url plutôt ?
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS source TEXT;
ALTER TABLE mollo_scores ADD COLUMN IF NOT EXISTS video_type TEXT;

-- 4. Index pour performance (optionnel)
CREATE INDEX IF NOT EXISTS idx_analysis_tasks_status ON analysis_tasks(status);
CREATE INDEX IF NOT EXISTS idx_metadata_media_type ON metadata_estimations(media_type);
