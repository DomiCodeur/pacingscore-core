import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ShowInfo {
  id: number;
  title: string;
  description: string;
  posterPath: string;
  backdropPath: string;
  firstAirDate: string;
  ageRating: string;
  pacingScore: number;
  tmdbData?: any;
}

@Injectable({
  providedIn: 'root'
})
export class YouTubeService {
  private apiAnalysisUrl = 'http://localhost:8080/api/analysis';
  private apiShowsUrl = 'http://localhost:8080/api/shows';

  constructor(private http: HttpClient) {}

  /**
   * Récupérer toutes les séries depuis la base Supabase
   */
  getShows(age: string = '0+', minScore: number = 0): Observable<ShowInfo[]> {
    return this.http.get<ShowInfo[]>(`${this.apiShowsUrl}`, {
      params: {
        age: age,
        minScore: minScore.toString()
      }
    });
  }

  /**
   * Rechercher des séries
   */
  searchShows(query: string, age: string = '0+'): Observable<ShowInfo[]> {
    return this.http.get<ShowInfo[]>(`${this.apiShowsUrl}/search`, {
      params: {
        q: query,
        age: age
      }
    });
  }

  /**
   * Recherche automatique de vidéos YouTube et analyse
   */
  crawlAndAnalyze(searchTerm: string): Observable<any[]> {
    return this.http.post<any[]>(`${this.apiAnalysisUrl}/crawl`, null, {
      params: { searchTerm }
    });
  }

  /**
   * Populate la base de données avec TMDB
   */
  populateFromTMDB(): Observable<string> {
    return this.http.post<string>(`${this.apiAnalysisUrl}/populate`, null, {
      responseType: 'text' as any
    });
  }
}