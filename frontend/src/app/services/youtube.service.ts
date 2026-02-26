import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface YouTubeVideoAnalysis {
  videoId: string;
  title: string;
  description: string;
  thumbnailUrl: string;
  videoUrl: string;
  pacingScore: number;
  ageRating: string;
}

export interface CrawlRequest {
  searchTerm: string;
}

@Injectable({
  providedIn: 'root'
})
export class YouTubeService {
  private apiUrl = 'http://localhost:8080/api/analysis';

  constructor(private http: HttpClient) {}

  /**
   * Recherche automatique de vidéos YouTube et analyse
   */
  crawlAndAnalyze(searchTerm: string): Observable<YouTubeVideoAnalysis[]> {
    const request: CrawlRequest = { searchTerm };
    return this.http.post<YouTubeVideoAnalysis[]>(`${this.apiUrl}/crawl`, null, {
      params: { searchTerm }
    });
  }

  /**
   * Populate la base de données avec des dessins animés
   */
  populateDatabase(): Observable<string> {
    return this.http.post<string>(`${this.apiUrl}/populate`, null, {
      responseType: 'text' as any
    });
  }

  /**
   * Recherche avec filtres
   */
  search(query: string, age: string = '0+', minScore: number = 0): Observable<YouTubeVideoAnalysis[]> {
    return this.http.get<YouTubeVideoAnalysis[]>(`${this.apiUrl}/search`, {
      params: {
        query,
        age: age,
        minScore: minScore.toString()
      }
    });
  }
}