import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface TMDBShow {
  id: number;
  name: string;
  poster_path: string;
  backdrop_path: string;
  first_air_date: string;
  overview: string;
  genre_ids: number[];
}

@Injectable({
  providedIn: 'root'
})
export class TMDBService {
  private baseUrl = 'https://api.themoviedb.org/3';
  private imageBaseUrl = 'https://image.tmdb.org/t/p';

  constructor(private http: HttpClient) {}

  searchShows(query: string): Observable<TMDBShow[]> {
    const params = {
      api_key: environment.tmdbApiKey,
      query,
      with_genres: '16', // Animation genre
      language: 'fr-FR'  // French results
    };

    return this.http.get<any>(`${this.baseUrl}/search/tv`, { params })
      .pipe(
        map(response => response.results),
        catchError(error => {
          console.error('TMDB Search Error:', error);
          return of([]);
        })
      );
  }

  getShowDetails(id: number): Observable<any> {
    const params = {
      api_key: environment.tmdbApiKey,
      language: 'fr-FR',
      append_to_response: 'images,videos'
    };

    return this.http.get(`${this.baseUrl}/tv/${id}`, { params });
  }

  getPosterUrl(path: string, size: string = 'w342'): string {
    if (!path) return '/assets/images/no-poster.jpg';
    return `${this.imageBaseUrl}/${size}${path}`;
  }

  getBackdropUrl(path: string, size: string = 'w1280'): string {
    if (!path) return '/assets/images/no-backdrop.jpg';
    return `${this.imageBaseUrl}/${size}${path}`;
  }

  // Cache for suggestions
  private suggestionCache = new Map<string, TMDBShow[]>();

  getSuggestions(query: string): Observable<TMDBShow[]> {
    // Check cache first
    const cached = this.suggestionCache.get(query);
    if (cached) return of(cached);

    return this.searchShows(query).pipe(
      tap(shows => {
        // Cache results
        this.suggestionCache.set(query, shows);
        
        // Clear old cache entries (simple cleanup)
        if (this.suggestionCache.size > 100) {
          const oldestKey = this.suggestionCache.keys().next().value;
          this.suggestionCache.delete(oldestKey);
        }
      })
    );
  }
}