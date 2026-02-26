-- Script pour populer automatiquement la base de données avec des vidéos YouTube
-- À exécuter via l'API ou manuellement

INSERT INTO video_analyses (
    video_id,
    title,
    description,
    thumbnail_url,
    video_url,
    pacing_score,
    age_rating,
    duration_minutes,
    created_at
) VALUES 
    -- Exemples de vidéos pour test
    ('dummy1', 'Calm Baby Cartoon', 'Dessin animé très calme pour bébés', 'https://img.youtube.com/vi/dummy1/mqdefault.jpg', 'https://youtube.com/watch?v=dummy1', 95, '0+', 5, NOW()),
    ('dummy2', 'Sweet Little Animals', 'Animation douce avec des animaux', 'https://img.youtube.com/vi/dummy2/mqdefault.jpg', 'https://youtube.com/watch?v=dummy2', 88, '3+', 7, NOW()),
    ('dummy3', 'Bedtime Stories', 'Histoires pour le coucher', 'https://img.youtube.com/vi/dummy3/mqdefault.jpg', 'https://youtube.com/watch?v=dummy3', 92, '0+', 10, NOW()),
    ('dummy4', 'Educational Cartoon', 'Dessin animé éducatif', 'https://img.youtube.com/vi/dummy4/mqdefault.jpg', 'https://youtube.com/watch?v=dummy4', 65, '6+', 12, NOW());

-- Créer une vue pour les recommandations
CREATE OR REPLACE VIEW video_recommendations AS
SELECT 
    *,
    CASE 
        WHEN pacing_score >= 90 THEN 'Très calme - Parfait pour les tout-petits'
        WHEN pacing_score >= 70 THEN 'Calme - Bon rythme adapté'
        WHEN pacing_score >= 50 THEN 'Modéré - À surveiller'
        WHEN pacing_score >= 30 THEN 'Stimulant - Attention au rythme'
        ELSE 'Très stimulant - Peut être trop intense'
    END AS pacing_label
FROM video_analyses
ORDER BY pacing_score DESC, created_at DESC;

-- Créer une table pour suivre les analyses automatiques
CREATE TABLE IF NOT EXISTS youtube_crawl_logs (
    id BIGSERIAL PRIMARY KEY,
    search_term VARCHAR(255) NOT NULL,
    video_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);