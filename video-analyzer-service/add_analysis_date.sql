-- Ajouter la colonne analysis_date à la table analysis_results
ALTER TABLE analysis_results
ADD COLUMN analysis_date TIMESTAMPTZ DEFAULT NOW();