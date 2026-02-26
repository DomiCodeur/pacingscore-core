import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { SupabaseService } from '../../services/supabase.service';

interface Show {
  id: string;
  video_path: string;
  pacing_score: number;
  cuts_per_minute: number;
  metadata: {
    age: string;
    style: string;
    poster?: string;
  };
}

@Component({
  selector: 'app-show-grid',
  template: `
    <div class="container mx-auto px-4 py-8">
      <!-- Hero Section -->
      <div class="mb-12 text-center">
        <h1 class="text-4xl font-bold mb-4 text-gray-800">PacingScore Kids</h1>
        <p class="text-xl text-gray-600">Le "Yuka" des dessins animés pour vos enfants</p>
      </div>

      <!-- Search Bar -->
      <div class="relative max-w-2xl mx-auto mb-12">
        <input 
          [formControl]="searchControl"
          type="text" 
          placeholder="Rechercher un dessin animé..." 
          class="w-full px-6 py-4 text-lg rounded-full border-2 border-purple-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all"
        >
        <span class="absolute right-6 top-1/2 transform -translate-y-1/2 text-gray-400">
          🔍
        </span>
      </div>

      <!-- Featured Shows Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12" *ngIf="!searchResults.length">
        <div *ngFor="let show of featuredShows" 
             class="show-card group relative rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300">
          <!-- Poster Image -->
          <div class="aspect-[2/3] w-full bg-gray-200 relative overflow-hidden">
            <img 
              [src]="show.metadata?.poster || getDefaultPoster(show.video_path)"
              [alt]="show.video_path"
              class="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-300"
            >
            <!-- Score Badge -->
            <div class="absolute top-4 right-4 w-16 h-16 rounded-full flex items-center justify-center"
                 [ngClass]="getScoreClass(show.pacing_score)">
              <span class="text-xl font-bold">{{ show.pacing_score }}%</span>
            </div>
            <!-- Age Badge -->
            <div class="absolute top-4 left-4 px-3 py-1 rounded-full text-sm font-semibold"
                 [ngClass]="getAgeClass(show.metadata?.age)">
              {{ show.metadata?.age }}
            </div>
          </div>
          <!-- Info Section -->
          <div class="p-4 bg-white">
            <h3 class="text-lg font-semibold mb-2">{{ show.video_path }}</h3>
            <p class="text-sm text-gray-600">{{ show.metadata?.style }}</p>
          </div>
        </div>
      </div>

      <!-- Search Results -->
      <div class="flex flex-col space-y-4" *ngIf="searchResults.length">
        <div *ngFor="let show of searchResults" 
             class="flex bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300">
          <!-- Left: Poster -->
          <div class="w-48 bg-gray-200 relative">
            <img 
              [src]="show.metadata?.poster || getDefaultPoster(show.video_path)"
              [alt]="show.video_path"
              class="w-full h-full object-cover"
            >
          </div>
          <!-- Right: Info -->
          <div class="flex-1 p-6 flex justify-between items-center">
            <div>
              <h3 class="text-xl font-semibold mb-2">{{ show.video_path }}</h3>
              <div class="flex items-center space-x-4">
                <span class="px-3 py-1 rounded-full text-sm font-semibold"
                      [ngClass]="getAgeClass(show.metadata?.age)">
                  {{ show.metadata?.age }}
                </span>
                <span class="text-gray-600">{{ show.metadata?.style }}</span>
              </div>
            </div>
            <!-- Score Circle -->
            <div class="w-24 h-24 rounded-full flex items-center justify-center mr-6"
                 [ngClass]="getScoreClass(show.pacing_score)">
              <span class="text-2xl font-bold">{{ show.pacing_score }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .show-card:hover {
      transform: translateY(-4px);
    }
  `]
})
export class ShowGridComponent implements OnInit {
  searchControl = new FormControl('');
  searchResults: Show[] = [];
  featuredShows: Show[] = [];

  constructor(private supabase: SupabaseService) {}

  ngOnInit() {
    // Load featured shows
    this.loadFeaturedShows();

    // Setup search
    this.searchControl.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(term => {
      if (term) {
        this.searchShows(term);
      } else {
        this.searchResults = [];
      }
    });
  }

  async loadFeaturedShows() {
    const { data, error } = await this.supabase.client
      .from('video_analyses')
      .select('*')
      .limit(8);

    if (data) {
      this.featuredShows = data;
    }
  }

  async searchShows(term: string) {
    const { data, error } = await this.supabase.client
      .from('video_analyses')
      .select('*')
      .ilike('video_path', `%${term}%`);

    if (data) {
      this.searchResults = data;
    }
  }

  getScoreClass(score: number): string {
    if (score >= 90) return 'bg-green-500 text-white';
    if (score >= 70) return 'bg-lime-500 text-white';
    if (score >= 50) return 'bg-yellow-500 text-white';
    if (score >= 30) return 'bg-orange-500 text-white';
    return 'bg-red-500 text-white';
  }

  getAgeClass(age: string): string {
    switch(age) {
      case '0+': return 'bg-green-100 text-green-800';
      case '3+': return 'bg-blue-100 text-blue-800';
      case '6+': return 'bg-yellow-100 text-yellow-800';
      case '10+': return 'bg-orange-100 text-orange-800';
      case '14+': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  getDefaultPoster(title: string): string {
    // On utilisera un service d'images plus tard
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(title)}&size=400&background=random`;
  }
}