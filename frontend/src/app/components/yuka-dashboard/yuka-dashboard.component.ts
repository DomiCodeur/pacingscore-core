import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { debounceTime, distinctUntilChanged, switchMap, catchError, of } from 'rxjs';
import { SpringBootService, Show } from '../../services/spring-boot.service';

@Component({
  selector: 'app-yuka-dashboard',
  template: `
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16 gap-6 flex-wrap">
          <!-- Logo -->
          <a href="#" class="flex items-center gap-3 text-decoration-none">
            <div class="w-11 h-11 bg-green-500 rounded-xl flex items-center justify-center text-white font-bold text-xl">
              🎬
            </div>
            <div>
              <h1 class="text-lg font-bold text-gray-900 leading-tight">Mollo</h1>
              <p class="text-xs text-gray-500 font-medium">Le score des dessins animés</p>
            </div>
          </a>

          <!-- Search Bar -->
          <div class="flex-1 max-w-xl">
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
              </span>
              <input 
                [formControl]="searchControl"
                type="text"
                placeholder="Rechercher un dessin animé..."
                class="w-full pl-12 pr-4 py-3 bg-gray-100 border-2 border-transparent rounded-xl focus:bg-white focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all duration-200 text-gray-900 placeholder-gray-400"
              >
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="bg-gradient-to-b from-green-50 to-white py-12 md:py-16">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <div class="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm mb-6">
          <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span class="text-sm font-semibold text-green-700">Nouveau : Données TMDB synchronisées</span>
        </div>
        
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 leading-tight">
          Vérifiez le rythme de montage de vos
          <span class="text-green-500">dessins animés</span>
        </h2>
        
        <p class="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
          Protégez l'attention de vos enfants. Découvrez rapidement si un contenu est adapté à leur âge.
        </p>

        <!-- Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div class="bg-white rounded-2xl p-6 shadow-sm">
            <div class="text-3xl font-bold text-green-500">{{ shows.length }}</div>
            <div class="text-sm text-gray-500 font-medium">Dessins animés</div>
          </div>
          <div class="bg-white rounded-2xl p-6 shadow-sm">
            <div class="text-3xl font-bold text-green-500">{{ getAverageScore().toFixed(1) }}</div>
            <div class="text-sm text-gray-500 font-medium">Score moyen</div>
          </div>
          <div class="bg-white rounded-2xl p-6 shadow-sm">
            <div class="text-3xl font-bold text-green-500">{{ getBestScore() }}</div>
            <div class="text-sm text-gray-500 font-medium">Meilleur score</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      <!-- Loading State -->
      <div *ngIf="loading" class="flex flex-col items-center justify-center py-20">
        <div class="animate-spin rounded-full h-16 w-16 border-4 border-green-500 border-t-transparent mb-4"></div>
        <p class="text-gray-500 font-medium animate-pulse">Récupération des données TMDB...</p>
      </div>

      <ng-container *ngIf="!loading">
        <!-- Filters -->
        <div class="flex flex-col gap-4 items-center mb-10">
          <!-- Rythme -->
          <div class="flex flex-wrap gap-2 justify-center">
            <span class="w-full text-center text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Rythme</span>
            <button 
              *ngFor="let filter of filters"
              (click)="applyFilter(filter)"
              [ngClass]="activeFilter === filter.id ? 'bg-green-500 text-white border-green-500 shadow-md' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'"
              class="px-4 py-2 rounded-full text-sm font-semibold border-2 transition-all duration-200"
            >
              {{ filter.label }}
            </button>
          </div>

          <!-- Âge -->
          <div class="flex flex-wrap gap-2 justify-center">
            <span class="w-full text-center text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Âge conseillé</span>
            <button 
              *ngFor="let age of ageFilters"
              (click)="applyAgeFilter(age.id)"
              [ngClass]="activeAgeFilter === age.id ? 'bg-blue-500 text-white border-blue-500 shadow-md' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'"
              class="px-4 py-2 rounded-full text-sm font-semibold border-2 transition-all duration-200"
            >
              {{ age.label }}
            </button>
          </div>
        </div>

        <!-- Results Header -->
        <div class="flex items-center justify-between mb-6 border-b border-gray-200 pb-4">
          <h3 class="text-xl font-bold text-gray-900" id="resultsTitle">
            {{ getResultsTitle() }}
          </h3>
          <span class="text-sm text-gray-500 font-medium">
            {{ filteredShows.length }} résultat{{ filteredShows.length > 1 ? 's' : '' }}
          </span>
        </div>

        <!-- Shows Grid -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-5">
          <div 
            *ngFor="let show of filteredShows"
            (click)="openModal(show)"
            class="group cursor-pointer"
          >
            <div class="relative rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <!-- Image Container -->
              <div class="aspect-[2/3] bg-gradient-to-br from-gray-100 to-gray-200 relative overflow-hidden">
                <!-- Badge Score -->
                <div class="absolute top-2 left-2 px-2.5 py-1 rounded-lg text-white text-[10px] font-black shadow-lg z-10"
                     [style.background]="getScoreBg(show.composite_score)">
                  {{ show.composite_score }}
                </div>

                <!-- Poster -->
                <img 
                  *ngIf="show.poster_path && !show.poster_path.includes('assets/')"
                  [src]="show.poster_path"
                  [alt]="show.title"
                  class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  loading="lazy"
                >
                
                <!-- Fallback if no image -->
                <div *ngIf="!show.poster_path || show.poster_path.includes('assets/')" 
                     class="w-full h-full flex flex-col items-center justify-center p-4 bg-gray-100">
                  <div class="text-3xl mb-2">🎬</div>
                  <div class="text-xs font-bold text-gray-400 text-center uppercase tracking-wider">{{ show.title }}</div>
                </div>

                <!-- Hover Overlay -->
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
                  <div class="bg-white text-gray-900 px-4 py-2 rounded-full text-xs font-bold shadow-lg">Détails</div>
                </div>
              </div>

              <!-- Info Section -->
              <div class="p-3 bg-white border-t border-gray-50">
                <h4 class="font-bold text-gray-900 text-sm mb-1 line-clamp-1">{{ show.title }}</h4>
                <div class="flex items-center gap-2 mb-2">
                   <span class="px-1.5 py-0.5 bg-gray-100 rounded text-[10px] font-bold text-gray-500">{{ show.age_recommendation || '0+' }}</span>
                   <span class="text-[10px] text-gray-400">⏱️ {{ show.average_shot_length || '?' }}s</span>
                </div>
                <div class="h-1 rounded-full overflow-hidden bg-gray-100">
                  <div class="h-full" [style.width]="show.composite_score + '%'" [style.background]="getScoreBg(show.composite_score)"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Results -->
        <div *ngIf="filteredShows.length === 0" class="text-center py-20">
          <div class="text-6xl mb-4">🔍</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-2">Aucun résultat trouvé</h3>
          <p class="text-gray-500">Essayez une autre recherche.</p>
        </div>
      </ng-container>
    </main>

    <!-- Modal Détails (Inchangée mais simplifiée) -->
    <div *ngIf="selectedShow" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" (click)="closeModal()"></div>
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden relative z-10 transition-all transform scale-100">
          <div class="h-32 p-6 flex flex-col justify-end text-white" [style.background]="getModalGradient(selectedShow.composite_score)">
              <h3 class="text-2xl font-black">{{ selectedShow.title }}</h3>
              <p class="text-sm opacity-90 font-medium">{{ selectedShow.evaluation_label }} • Score {{ selectedShow.composite_score }}/100</p>
          </div>
          <div class="p-8">
              <p class="text-gray-600 mb-8 leading-relaxed font-medium">
                Cette série a un rythme de montage <strong>{{ selectedShow.evaluation_label.toLowerCase() }}</strong> pour le développement cognitif des jeunes enfants.
              </p>
              <div class="grid grid-cols-2 gap-4 mb-8">
                  <div class="bg-gray-50 p-4 rounded-2xl border border-gray-100">
                      <div class="text-xs font-bold text-gray-400 uppercase mb-1">Âge conseillé</div>
                      <div class="text-xl font-black text-gray-900">{{ selectedShow.age_recommendation || 'Tout public' }}</div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-2xl border border-gray-100">
                      <div class="text-xs font-bold text-gray-400 uppercase mb-1">Moyenne Plan</div>
                      <div class="text-xl font-black text-gray-900">{{ selectedShow.average_shot_length || '?' }}s</div>
                  </div>
              </div>
              <button (click)="closeModal()" class="w-full py-4 bg-gray-900 text-white rounded-2xl font-bold hover:bg-gray-800 transition-colors shadow-lg">
                Fermer
              </button>
          </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-100 py-10">
      <div class="max-w-7xl mx-auto px-4 text-center">
        <div class="text-gray-400 text-xs font-bold tracking-widest uppercase mb-2">Mollo Project</div>
        <p class="text-gray-400 text-[10px]">Utilise l'API TMDB pour les métadonnées et images.</p>
      </div>
    </footer>
  `,
  styles: [`
    :host { display: block; background: #fafafa; min-h: 100vh; }
    .line-clamp-1 { display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
  `]
})
export class YukaDashboardComponent implements OnInit {
  shows: Show[] = [];
  filteredShows: Show[] = [];
  loading = false;
  searchControl = new FormControl('');
  selectedShow: Show | null = null;
  activeFilter = 'all';

    filters = [
    { id: 'all', label: 'Tous' },
    { id: 'excellent', label: 'Lent (80+)' },
    { id: 'good', label: 'Bon (60-80)' },
    { id: 'moderate', label: 'Moyen (40-60)' },
    { id: 'fast', label: 'Énergique (<40)' }
  ];

  ageFilters = [
    { id: 'all', label: 'Tous âges' },
    { id: '0+', label: '0+' },
    { id: '3+', label: '3+' },
    { id: '6+', label: '6+' },
    { id: '10+', label: '10+' }
  ];
  activeAgeFilter = 'all';

  constructor(private springBootService: SpringBootService) {}

  ngOnInit() {
    this.loadShows();

    this.searchControl.valueChanges.pipe(
      debounceTime(400),
      distinctUntilChanged(),
      switchMap((term) => {
        this.loading = true;
        if (term) return this.springBootService.searchShows(term);
        return this.springBootService.getAllShows();
      }),
      catchError(() => {
        this.loading = false;
        return of([]);
      })
    ).subscribe((shows) => {
      this.loading = false;
      this.shows = shows;
      this.applyCurrentFilter();
    });
  }

  loadShows() {
    this.loading = true;
    this.springBootService.getAllShows().subscribe({
      next: (shows) => {
        this.shows = shows;
        this.filteredShows = shows;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  applyAgeFilter(ageId: string) {
    this.activeAgeFilter = ageId;
    this.applyAllFilters();
  }

  applyFilter(filter: any) {
    this.activeFilter = filter.id;
    this.applyAllFilters();
  }

  applyAllFilters() {
    let results = [...this.shows];

    // Filtrage par rythme (Pacing)
    if (this.activeFilter === 'excellent') {
      results = results.filter(s => s.composite_score >= 80);
    } else if (this.activeFilter === 'good') {
      results = results.filter(s => s.composite_score >= 60 && s.composite_score < 80);
    } else if (this.activeFilter === 'moderate') {
      results = results.filter(s => s.composite_score >= 40 && s.composite_score < 60);
    } else if (this.activeFilter === 'fast') {
      results = results.filter(s => s.composite_score < 40);
    }

    // Filtrage par âge
    if (this.activeAgeFilter !== 'all') {
      results = results.filter(s => s.age_recommendation === this.activeAgeFilter);
    }

    this.filteredShows = results;
  }

  applyCurrentFilter() {
    this.applyFilter({ id: this.activeFilter });
  }

  getResultsTitle(): string {
    if (this.searchControl.value) return `Recherche : ${this.searchControl.value}`;
    return 'Analyses Récentes';
  }

  getScoreBg(score: number): string {
    if (score >= 80) return '#22c55e'; // green-500
    if (score >= 60) return '#84cc16'; // lime-500
    if (score >= 40) return '#f59e0b'; // amber-500
    return '#ef4444'; // red-500
  }

  getModalGradient(score: number): string {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#84cc16';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  }

  getAverageScore(): number {
    if (this.shows.length === 0) return 0;
    return this.shows.reduce((sum, s) => sum + s.composite_score, 0) / this.shows.length;
  }

  getBestScore(): string {
    if (this.shows.length === 0) return '0';
    return Math.max(...this.shows.map(s => s.composite_score)).toString();
  }

  openModal(show: Show) {
    this.selectedShow = show;
  }

  closeModal() {
    this.selectedShow = null;
  }
}
