-- 1. Nettoyage des titres génériques
DELETE FROM video_analyses 
WHERE title ILIKE '%film complet%' 
   OR title ILIKE '%film d''animation%'
   OR title ILIKE '%animation film%'
   OR title ILIKE '%streaming%';

-- 2. Suppression des doublons (garder celui avec le meilleur score)
WITH ranked AS (
  SELECT 
    *,
    ROW_NUMBER() OVER (PARTITION BY series_title ORDER BY pacing_score DESC) as rn
  FROM video_analyses
)
DELETE FROM video_analyses 
WHERE id IN (
  SELECT id FROM ranked WHERE rn > 3
);

-- 3. Correction des scores pour les séries cultes
UPDATE video_analyses
SET pacing_score = 85
WHERE title ILIKE '%babar%';

UPDATE video_analyses
SET pacing_score = 75
WHERE title ILIKE '%peppa pig%';

UPDATE video_analyses
SET pacing_score = 65
WHERE title ILIKE '%petit ours brun%';

UPDATE video_analyses
SET pacing_score = 45
WHERE title ILIKE '%trotro%';

-- 4. Correction des catégories d'âge
UPDATE video_analyses
SET age_rating = 
  CASE 
    WHEN title ILIKE ANY(ARRAY['peppa pig%', 'petit ours brun%', 'trotro%']) THEN '0+'
    WHEN title ILIKE ANY(ARRAY['babar%', 'tchoupi%']) THEN '3+'
    WHEN title ILIKE ANY(ARRAY['disney%', 'pixar%']) THEN '6+'
    ELSE age_rating
  END;

-- 5. S'assurer que les métadonnées TMDB sont présentes
UPDATE video_analyses
SET tmdb_data = jsonb_build_object('title', title)
WHERE tmdb_data IS NULL;