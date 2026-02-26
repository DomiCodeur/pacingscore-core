export const TMDB_CONFIG = {
  BASE_URL: 'https://api.themoviedb.org/3',
  BASE_IMG_URL: 'https://image.tmdb.org/t/p',
  POSTER_SIZES: {
    TINY: 'w92',
    SMALL: 'w154',
    MEDIUM: 'w342',
    LARGE: 'w500',
    ORIGINAL: 'original'
  },
  BACKDROP_SIZES: {
    SMALL: 'w300',
    MEDIUM: 'w780',
    LARGE: 'w1280',
    ORIGINAL: 'original'
  },
  DEFAULT_LANG: 'fr-FR',
  ANIMATION_GENRE_ID: 16,  // ID du genre "Animation" sur TMDB
  AGE_RATINGS: {
    'TV-Y': '0+',    // Pour tous
    'TV-Y7': '3+',   // À partir de 3 ans
    'TV-G': '6+',    // À partir de 6 ans
    'TV-PG': '10+',  // À partir de 10 ans
    'TV-14': '14+'   // À partir de 14 ans
  }
};