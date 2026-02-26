import { Component } from '@angular/core';
import { ShowService } from '../../services/show.service';

@Component({
  selector: 'app-admin-panel',
  template: `
    <div class="admin-panel p-6 bg-white rounded-xl shadow-lg max-w-4xl mx-auto">
      <h2 class="text-2xl font-bold mb-6 text-gray-800">🎯 Configuration Automatique</h2>

      <!-- Section Populate -->
      <div class="mb-8 p-4 bg-purple-50 rounded-lg">
        <h3 class="text-lg font-semibold mb-3 text-purple-800">🚀 Populer la base de données</h3>
        <p class="text-gray-600 mb-4">Automatiquement rechercher et analyser des dessins animés enfants</p>
        
        <button 
          (click)="populate()"
          [disabled]="isLoading"
          class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-all"
        >
          {{ isLoading ? 'Analyse en cours...' : 'Démarrer l\'analyse automatique' }}
        </button>

        <div *ngIf="progress > 0" class="mt-4">
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div class="bg-purple-600 h-2.5 rounded-full transition-all" [style.width]="progress + '%'"></div>
          </div>
          <p class="text-sm text-gray-600 mt-1">Progression: {{ progress }}%</p>
        </div>
      </div>

      <!-- Section Recherche Personnalisée -->
      <div class="mb-8 p-4 bg-blue-50 rounded-lg">
        <h3 class="text-lg font-semibold mb-3 text-blue-800">🔍 Recherche Personnalisée</h3>
        
        <div class="flex gap-4 mb-4">
          <input 
            type="text" 
            [(ngModel)]="searchTerm"
            placeholder="Ex: dessin animé calm bébé"
            class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          >
          <button 
            (click)="search()"
            [disabled]="!searchTerm || isLoading"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-all"
          >
            Chercher
          </button>
        </div>
      </div>

      <!-- Résultats -->
      <div *ngIf="results.length > 0" class="p-4 bg-green-50 rounded-lg">
        <h3 class="text-lg font-semibold mb-3 text-green-800">📊 Résultats</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div *ngFor="let video of results" class="bg-white p-3 rounded-lg shadow">
            <h4 class="font-semibold text-sm mb-2 truncate">{{ video.title }}</h4>
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-1 text-xs font-bold rounded-full"
                [ngClass]="getScoreClass(video.pacingScore)">
                {{ video.pacingScore }}%
              </span>
              <span class="px-2 py-1 text-xs font-bold rounded-full bg-blue-100 text-blue-800">
                {{ video.ageRating }}
              </span>
            </div>
            <a [href]="video.videoUrl" target="_blank" 
               class="text-blue-600 text-xs hover:underline">
              Voir la vidéo →
            </a>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div *ngIf="message" class="mt-4 p-3 rounded-lg" 
           [ngClass]="error ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'">
        {{ message }}
      </div>
    </div>
  `
})
export class AdminPanelComponent {
  searchTerm: string = '';
  results: any[] = [];
  isLoading: boolean = false;
  progress: number = 0;
  message: string = '';
  error: boolean = false;

  constructor(private showService: ShowService) {}

  populate(): void {
    this.isLoading = true;
    this.progress = 0;
    this.message = 'Démarrage de l\'analyse automatique TMDB...';
    this.error = false;

    this.showService.populateFromTMDB().subscribe({
      next: (response) => {
        this.message = response;
        this.isLoading = false;
        this.progress = 100;
      },
      error: (err) => {
        this.message = 'Erreur: ' + err.message;
        this.error = true;
        this.isLoading = false;
      }
    });
  }

  search(): void {
    if (!this.searchTerm.trim()) return;

    this.isLoading = true;
    this.message = 'Recherche en cours...';
    this.error = false;
    this.results = [];

    this.showService.crawlAndAnalyze(this.searchTerm).subscribe({
      next: (videos) => {
        this.results = videos;
        this.message = `${videos.length} vidéos trouvées et analysées`;
        this.isLoading = false;
      },
      error: (err) => {
        this.message = 'Erreur lors de la recherche: ' + err.message;
        this.error = true;
        this.isLoading = false;
      }
    });
  }

  getScoreClass(score: number): string {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 70) return 'bg-lime-100 text-lime-800';
    if (score >= 50) return 'bg-yellow-100 text-yellow-800';
    if (score >= 30) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  }
}