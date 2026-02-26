import { Component, Input } from '@angular/core';
import { TMDBShow } from '../../services/tmdb.service';

@Component({
  selector: 'app-show-card',
  template: `
    <div class="group relative rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300">
      <!-- Image Container -->
      <div class="aspect-[2/3] w-full bg-gray-200 relative overflow-hidden">
        <!-- Poster avec lazy loading et effet de transition -->
        <img 
          [src]="show.poster_path ? getPosterUrl(show.poster_path) : 'assets/images/no-poster.svg'"
          [alt]="show.name"
          class="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
          loading="lazy"
        >
        
        <!-- Overlay gradient -->
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        </div>

        <!-- Score Badge -->
        <div class="absolute top-2 right-2">
          <app-score-badge 
            [score]="pacingScore" 
            [ageRating]="getAgeRating()"
          ></app-score-badge>
        </div>

        <!-- Année -->
        <div class="absolute bottom-2 left-2 text-white text-sm font-medium">
          {{ getYear(show.first_air_date) }}
        </div>
      </div>

      <!-- Info Section -->
      <div class="p-4 bg-white">
        <h3 class="text-lg font-semibold mb-1 group-hover:text-purple-600 transition-colors">
          {{ show.name }}
        </h3>
        
        <!-- Tags -->
        <div class="flex flex-wrap gap-2 mt-2">
          <span *ngFor="let tag of getTags()" 
                class="px-2 py-1 text-xs rounded-full"
                [ngClass]="getTagClass(tag)">
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- Action Overlay (visible au hover) -->
      <div class="absolute inset-0 bg-black/75 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <button class="px-6 py-3 bg-purple-600 text-white rounded-full transform -translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
          Voir les détails
        </button>
      </div>
    </div>
  `
})
export class ShowCardComponent {
  @Input() show!: TMDBShow;
  @Input() pacingScore: number = 0;

  getPosterUrl(path: string): string {
    return `https://image.tmdb.org/t/p/w342${path}`;
  }

  getYear(date: string): string {
    return date ? new Date(date).getFullYear().toString() : 'N/A';
  }

  getAgeRating(): string {
    if (this.pacingScore >= 90) return '0+';
    if (this.pacingScore >= 70) return '3+';
    if (this.pacingScore >= 50) return '6+';
    if (this.pacingScore >= 30) return '10+';
    return '14+';
  }

  getTags(): string[] {
    const tags = [];
    if (this.pacingScore >= 90) tags.push('Très Calme');
    else if (this.pacingScore >= 70) tags.push('Calme');
    else if (this.pacingScore >= 50) tags.push('Modéré');
    else if (this.pacingScore >= 30) tags.push('Stimulant');
    else tags.push('Très Stimulant');
    
    return tags;
  }

  getTagClass(tag: string): string {
    switch(tag) {
      case 'Très Calme': return 'bg-green-100 text-green-800';
      case 'Calme': return 'bg-lime-100 text-lime-800';
      case 'Modéré': return 'bg-yellow-100 text-yellow-800';
      case 'Stimulant': return 'bg-orange-100 text-orange-800';
      case 'Très Stimulant': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }
}