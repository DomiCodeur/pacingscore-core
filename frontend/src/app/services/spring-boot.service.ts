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
}

@Injectable({
  providedIn: 'root'
})
export class SpringBootService {
  
  private apiUrl = 'http://localhost:8080/api';
  
  constructor(private http: HttpClient) {}
  
  /**
   * Récupérer tous les dessins animés depuis l'API Spring Boot
   */
  getAllShows(): Observable<Show[]> {
    return this.http.get<Show[]>(`${this.apiUrl}/shows`);
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
}
