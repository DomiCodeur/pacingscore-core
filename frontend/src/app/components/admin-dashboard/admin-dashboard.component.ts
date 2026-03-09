import { Component, OnInit } from '@angular/core';
import { AnalysisService, FailedTask } from '../../services/analysis.service';
import { FormControl } from '@angular/forms';

@Component({
  selector: 'app-admin-dashboard',
  template: `
    <div class="min-h-screen bg-gray-50 p-6">
      <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-2xl shadow-sm p-6 mb-6 border border-gray-100">
          <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <span class="text-3xl">🔧</span>
            Administration - Tâches échouées
          </h1>
          <p class="text-gray-500 mt-2">Inspectez et relancez les analyses qui ont échoué</p>
        </div>

        <!-- Loading -->
        <div *ngIf="loading" class="flex justify-center py-20">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
        </div>

        <!-- No failed tasks -->
        <div *ngIf="!loading && failedTasks.length === 0" class="bg-white rounded-2xl shadow-sm p-12 text-center border border-gray-100">
          <div class="text-6xl mb-4">✅</div>
          <h2 class="text-xl font-bold text-gray-900 mb-2">Aucune tâche échouée</h2>
          <p class="text-gray-500">Toutes les analyses se sont déroulées correctement.</p>
        </div>

        <!-- Failed tasks table -->
        <div *ngIf="!loading && failedTasks.length > 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
            <span class="font-semibold text-gray-700">{{ failedTasks.length }} tâche(s) échouée(s)</span>
            <button (click)="loadFailedTasks()" class="text-sm text-blue-600 hover:text-blue-800 font-medium">
              Rafraîchir
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">TMDB ID</th>
                  <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Titre</th>
                  <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Erreur</th>
                  <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">URL manuelle</th>
                  <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr *ngFor="let task of failedTasks" [class.hidden]="task._removing">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <code class="text-sm bg-gray-100 px-2 py-1 rounded text-gray-800 font-mono">{{ task.tmdb_id }}</code>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm font-medium text-gray-900">{{ task.title || 'Inconnu' }}</div>
                    <div *ngIf="task.metadata?.media_type" class="text-xs text-gray-500">
                      {{ task.metadata.media_type === 'movie' ? 'Film' : 'Série' }}
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="text-sm text-red-600 max-w-xs truncate" [title]="task.error_message">{{ task.error_message || 'Aucune erreur' }}</div>
                  </td>
                  <td class="px-6 py-4">
                    <input 
                      type="text" 
                      [(ngModel)]="task.manualUrl"
                      [ngModelOptions]="{standalone: true}"
                      placeholder="https://..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    />
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <button 
                      (click)="retryTask(task)"
                      [disabled]="retrying === task.id"
                      class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span *ngIf="retrying === task.id" class="flex items-center gap-2">
                        <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Relance...
                      </span>
                      <span *ngIf="retrying !== task.id">Relancer</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .hidden { display: none; }
    code { font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; }
  `]
})
export class AdminDashboardComponent implements OnInit {
  failedTasks: FailedTask[] = [];
  loading = false;
  retrying: string | null = null;

  constructor(private analysisService: AnalysisService) {}

  ngOnInit(): void {
    this.loadFailedTasks();
  }

  loadFailedTasks(): void {
    this.loading = true;
    this.analysisService.getFailedTasks(100).subscribe({
      next: (tasks) => {
        this.failedTasks = tasks.map(t => ({ ...t, manualUrl: '', _removing: false }));
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur chargement tâches échouées', err);
        this.loading = false;
        this.failedTasks = [];
      }
    });
  }

  retryTask(task: FailedTask): void {
    if (!task.manualUrl && task.manualUrl !== '') {
      // Could show a warning but we'll proceed without manual URL
    }

    this.retrying = task.id;

    const manualUrl = task.manualUrl && task.manualUrl.trim() ? task.manualUrl.trim() : undefined;
    this.analysisService.retryTask(task.id, manualUrl).subscribe({
      next: (result) => {
        if (result.success) {
          // Mark as removing visually
          task._removing = true;
          // Remove from array after animation
          setTimeout(() => {
            this.failedTasks = this.failedTasks.filter(t => t.id !== task.id);
          }, 300);
        } else {
          alert('Erreur lors de la relance: ' + (result.error || 'Unknown'));
        }
        this.retrying = null;
      },
      error: (err) => {
        console.error('Erreur retryTask', err);
        alert('Erreur réseau lors de la relance');
        this.retrying = null;
      }
    });
  }
}
