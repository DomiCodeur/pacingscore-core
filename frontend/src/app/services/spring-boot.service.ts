import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Show {
  id: number;
  title: string;
  poster_path: string;
  backdrop_path: string;
  composite_score: number;
  average_shot_length: number | null;
  num_scenes: number | null;
  evaluation_label: string;
  evaluation_description: string;
  evaluation_color: 'green' | 'lime' | 'yellow' | 'red';
  age_recommendation: string;
  description: string;
  analysis_details: any | null;
  video_path: string;
  is_verified: boolean;
  tmdb_id: string;
  media_type?: string; // 'movie' ou 'tv'
  video_duration?: number | null;
  cuts_per_minute?: number | null;
  motion_intensity?: number | null;
  source?: string; // 'youtube', 'dailymotion', etc.
  video_type?: string; // 'episode', 'film', 'extrait', etc.
}

@Injectable({
  providedIn: 'root'
})
export class SpringBootService {
  
  private apiUrl = '/api';
  
  constructor(private http: HttpClient) {}
  
  /**
   * Récupérer tous les dessins animés depuis l'API Spring Boot
   * (sans pagination)
   */
  getAllShows(): Observable<Show[]> {
    // Par souci de compatibilité, retourne tout (limité par le back à 10000)
    return this.http.get<Show[]>(`${this.apiUrl}/shows?limit=10000`);
  }

  /**
   * Récupérer les dessins animés avec pagination
   * @param limit nombre d'éléments par page
   * @param offset décalage (page * limit)
   * @param age filtre d'âge (défaut "0+")
   * @param minScore score minimum
   * @param search recherche textuelle
   * @param type type de média (movie/tv)
   * @param verified si true, ne retourne que les shows avec score réel (analysés)
   */
  getAllShowsPaginated(limit: number, offset: number, age: string = 'all', minScore: number = 0, search?: string, type?: string, verified?: boolean): Observable<Show[]> {
    let url = `${this.apiUrl}/shows?limit=${limit}&offset=${offset}&minScore=${minScore}`;
    if (age && age !== 'all') {
      url += `&age=${encodeURIComponent(age)}`;
    }
    if (search) {
      url += `&search=${encodeURIComponent(search)}`;
    }
    if (type) {
      url += `&type=${type}`;
    }
    if (verified) {
      url += `&verified=true`;
    }
    return this.http.get<Show[]>(url);
  }
  
  /**
   * Récupérer le nombre total de shows réellement analysés (score réel)
   */
  getVerifiedShowsCount(): Observable<{count: number}> {
    return this.http.get<{count: number}>(`${this.apiUrl}/shows/count/verified`);
  }
  
  /**
   * Rechercher des dessins animés
   */
  searchShows(query: string): Observable<Show[]> {
    return this.http.get<Show[]>(`${this.apiUrl}/shows?search=${query}`);
  }
  
  /**
   * Filtrer par score
   */
  filterByScore(minScore: number, maxScore?: number): Observable<Show[]> {
    let url = `${this.apiUrl}/shows?minScore=${minScore}`;
    if (maxScore) {
      url += `&maxScore=${maxScore}`;
    }
    return this.http.get<Show[]>(url);
  }
  
  /**
   * Filtrer par âge recommandé
   */
  filterByAge(age: string): Observable<Show[]> {
    return this.http.get<Show[]>(`${this.apiUrl}/shows?age=${age}`);
  }
  
  /**
   * Récupérer un dessin animé par ID
   */
  getShowById(id: number): Observable<Show | undefined> {
    return this.http.get<Show | undefined>(`${this.apiUrl}/shows/${id}`);
  }
  
  /**
   * Récupérer les derniers shows ajoutés
   * @param limit nombre d'éléments
   * @param type filtre optionnel 'movie' ou 'tv'
   */
  getLatestShows(limit: number = 10, type?: 'movie' | 'tv'): Observable<Show[]> {
    let url = `${this.apiUrl}/shows/latest?limit=${limit}`;
    if (type) {
      url += `&type=${type}`;
    }
    return this.http.get<Show[]>(url);
  }
}
