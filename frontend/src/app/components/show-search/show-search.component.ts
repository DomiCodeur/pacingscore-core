import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { debounceTime, distinctUntilChanged, switchMap, tap } from 'rxjs/operators';
import { TMDBService, TMDBShow } from '../../services/tmdb.service';
import { SupabaseService } from '../../services/supabase.service';

@Component({
  selector: 'app-show-search',
  template: `
    <div class="relative w-full max-w-2xl mx-auto">
      <!-- Search Input -->
      <div class="relative">
        <input 
          [formControl]="searchControl"
          type="text" 
          placeholder="Rechercher un dessin animé..."
          class="w-full px-6 py-4 text-lg rounded-full border-2 border-purple-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all"
          (focus)="showSuggestions = true"
          (blur)="onBlur()"
        >
        <span class="absolute right-6 top-1/2 transform -translate-y-1/2 text-gray-400">
          🔍
        </span>
      </div>

      <!-- Suggestions Dropdown -->
      <div *ngIf="showSuggestions && (suggestions$ | async)?.length"
           class="absolute w-full mt-2 bg-white rounded-2xl shadow-2xl overflow-hidden z-50 animate-fade-in">
        
        <div *ngFor="let show of suggestions$ | async" 
             class="flex items-center p-4 hover:bg-purple-50 transition-colors cursor-pointer border-b last:border-0"
             (mousedown)="selectShow(show)">
          
          <!-- Show Poster -->
          <div class="w-16 h-24 bg-gray-200 rounded-lg overflow-hidden">
            <img [src]="tmdb.getPosterUrl(show.poster_path, 'w92')" 
                 [alt]="show.name"
                 class="w-full h-full object-cover">
          </div>

          <!-- Show Info -->
          <div class="ml-4 flex-1">
            <h4 class="font-semibold text-gray-900">{{ show.name }}</h4>
            <p class="text-sm text-gray-500">
              {{ show.first_air_date | date:'yyyy' }}
            </p>
          </div>

          <!-- PacingScore Badge (if exists) -->
          <div *ngIf="showScores[show.id]" 
               class="ml-4 w-14 h-14 rounded-full flex items-center justify-center text-white font-bold"
               [ngClass]="getScoreClass(showScores[show.id])">
            {{ showScores[show.id] }}%
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .animate-fade-in {
      animation: fadeIn 0.2s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class ShowSearchComponent implements OnInit {
  searchControl = new FormControl('');
  suggestions$ = this.searchControl.valueChanges.pipe(
    debounceTime(300),
    distinctUntilChanged(),
    switchMap(term => term ? this.tmdb.getSuggestions(term) : [])
  );
  showSuggestions = false;
  showScores: {[key: number]: number} = {};

  constructor(
    public tmdb: TMDBService,
    private supabase: SupabaseService
  ) {}

  ngOnInit() {
    // Load initial scores for caching
    this.loadPacingScores();
  }

  async loadPacingScores() {
    const { data } = await this.supabase.client
      .from('video_analyses')
      .select('tmdb_id, pacing_score');
    
    if (data) {
      this.showScores = data.reduce((acc, item) => ({
        ...acc,
        [item.tmdb_id]: item.pacing_score
      }), {});
    }
  }

  onBlur() {
    // Small delay to allow click events on suggestions
    setTimeout(() => {
      this.showSuggestions = false;
    }, 200);
  }

  async selectShow(show: TMDBShow) {
    // If we don't have a score for this show yet
    if (!this.showScores[show.id]) {
      // Get show details from TMDB
      const details = await this.tmdb.getShowDetails(show.id).toPromise();
      
      // Calculate initial pacing score (placeholder)
      const defaultScore = 75;  // We'll replace this with real analysis
      
      // Store in Supabase
      await this.supabase.client
        .from('video_analyses')
        .upsert({
          tmdb_id: show.id,
          video_path: show.name,
          pacing_score: defaultScore,
          cuts_per_minute: 5,
          metadata: {
            poster_path: show.poster_path,
            backdrop_path: show.backdrop_path,
            overview: show.overview,
            first_air_date: show.first_air_date,
            tmdb_data: details
          }
        });

      // Update local cache
      this.showScores[show.id] = defaultScore;
    }

    // Clear search
    this.searchControl.setValue('');
    this.showSuggestions = false;
  }

  getScoreClass(score: number): string {
    if (score >= 90) return 'bg-green-500';
    if (score >= 70) return 'bg-lime-500';
    if (score >= 50) return 'bg-yellow-500';
    if (score >= 30) return 'bg-orange-500';
    return 'bg-red-500';
  }
}