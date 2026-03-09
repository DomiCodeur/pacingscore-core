import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FailedTask {
  id: string;
  tmdb_id: string;
  title?: string;
  error_message?: string;
  created_at?: string;
  metadata?: any;
}

export interface RetryResult {
  success: boolean;
  task_id: string;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AnalysisService {
  private apiUrl = '/api/analysis';

  constructor(private http: HttpClient) {}

  /**
   * Récupère la liste des tâches d'analyse échouées
   * @param limit nombre maximum de résultats (optionnel)
   * @param tmdbId filtre optionnel sur un TMDB ID spécifique
   */
  getFailedTasks(limit?: number, tmdbId?: string): Observable<FailedTask[]> {
    let url = `${this.apiUrl}/failed-tasks`;
    const params: any = {};
    if (limit) params.limit = limit;
    if (tmdbId) params.tmdbId = tmdbId;

    // Construire l'URL avec paramètres de requête
    const firstParam = Object.keys(params).length > 0 ? '?' : '';
    const queryString = Object.entries(params)
      .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
      .join('&');
    url = queryString ? url + firstParam + queryString : url;

    return this.http.get<FailedTask[]>(url);
  }

  /**
   * Relance une tâche échouée (la remet en état 'pending')
   * @param taskId ID de la tâche à relancer
   */
  retryTask(taskId: string, manualUrl?: string): Observable<RetryResult> {
    const body: any = {};
    if (manualUrl && manualUrl.trim()) {
      body.manualUrl = manualUrl.trim();
    }
    return this.http.post<RetryResult>(`${this.apiUrl}/tasks/${taskId}/retry`, body);
  }
}
