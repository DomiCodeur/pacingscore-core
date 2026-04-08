import { Component, OnInit } from '@angular/core';
import { SpringBootService, Show } from '../../services/spring-boot.service';

@Component({
  selector: 'app-show-grid',
  template: `
    <div class="container mx-auto px-4 py-8">
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-2">Galerie des dessins animés analysés</h2>
        <p class="text-gray-600">Données issues de la vue shows_verified (TMDB + analyse vidéo)</p>
      </div>

      <!-- Loading -->
      <div *ngIf="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent"></div>
      </div>

      <!-- Grid -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5" *ngIf="!loading">
        <div *ngFor="let show of shows" class="group cursor-pointer">
          <div class="relative rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div class="aspect-[2/3] bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
              <!-- Badge score -->
              <div class="absolute top-2 left-2 flex flex-col gap-1 z-10">
                <div class="px-2.5 py-1 rounded-lg text-white text-[10px] font-black shadow-lg"
                     [style.background]="getScoreBg(show.composite_score)">
                  {{ show.composite_score }}
                </div>
                <div *ngIf="show.video_type" class="px-1.5 py-0.5 rounded text-[9px] font-semibold text-gray-700 bg-white/90 backdrop-blur shadow-sm self-start">
                  {{ getVideoTypeLabel(show.video_type) }}
                </div>
              </div>

              <!-- Poster -->
              <img *ngIf="show.poster_path && !show.poster_path.includes('assets/')"
                   [src]="show.poster_path"
                   [alt]="show.title"
                   class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                   loading="lazy">
              <div *ngIf="!show.poster_path || show.poster_path.includes('assets/')"
                   class="w-full h-full flex flex-col items-center justify-center p-4 bg-gray-100">
                <div class="text-3xl mb-2">🎬</div>
                <div class="text-xs font-bold text-gray-400 text-center uppercase tracking-tighter">{{ show.title }}</div>
              </div>
            </div>

            <!-- Info -->
            <div class="p-3 bg-white border-t border-gray-50">
              <h4 class="font-bold text-gray-900 text-sm mb-1 line-clamp-1">{{ show.title }}</h4>
              <div class="flex items-center gap-2 mb-2 flex-wrap">
                <span class="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] font-bold text-gray-500">{{ show.age_recommendation || '0+' }}</span>
                <span *ngIf="show.target_developmental_age" class="px-1.5 py-0.5 bg-blue-100 rounded text-[10px] font-bold text-blue-600">{{ show.target_developmental_age }}</span>
                <span class="text-[10px] text-gray-400">⏱️ {{ show.average_shot_length || '?' }}s</span>
              </div>
              <div class="h-1 rounded-full overflow-hidden bg-gray-100">
                <div class="h-full" [style.width]="show.composite_score + '%'" [style.background]="getScoreBg(show.composite_score)"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No results -->
      <div *ngIf="!loading && shows.length === 0" class="text-center py-20">
        <div class="text-6xl mb-4">🔍</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Aucun résultat</h3>
        <p class="text-gray-500">Aucun dessin animé analysé pour le moment.</p>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; background: #fafafa; min-height: 100vh; }
    .line-clamp-1 { display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
  `]
})
export class ShowGridComponent implements OnInit {
  shows: Show[] = [];
  loading = false;

  constructor(private springBootService: SpringBootService) {}

  ngOnInit() {
    this.loadShows();
  }

  loadShows(): void {
    this.loading = true;
    this.springBootService.getAllShows().subscribe({
      next: (shows) => {
        this.shows = shows;
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur chargement grille', err);
        this.loading = false;
        this.shows = [];
      }
    });
  }

  getScoreBg(score: number): string {
    if (score >= 80) return '#22c55e'; // green-500
    if (score >= 60) return '#84cc16'; // lime-500
    if (score >= 40) return '#f59e0b'; // amber-500
    return '#ef4444'; // red-500
  }

  getVideoTypeLabel(type: string): string {
    const labels: {[key: string]: string} = {
      'episode': 'Épisode',
      'film': 'Film',
      'movie': 'Film',
      'extrait': 'Extrait',
      'trailer': 'Bande-annonce',
      'full': 'Complet'
    };
    return labels[type] || type;
  }
}
