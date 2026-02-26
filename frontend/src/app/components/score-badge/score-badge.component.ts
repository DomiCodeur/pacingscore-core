import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-score-badge',
  template: `
    <div class="relative">
      <!-- Cercle principal -->
      <div class="w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300"
           [ngClass]="getBgClass()">
        <!-- Score -->
        <span class="text-xl font-bold text-white">{{ score }}%</span>
        
        <!-- Badge d'âge (si présent) -->
        <div *ngIf="ageRating" 
             class="absolute -top-2 -right-2 bg-white rounded-full px-2 py-1 text-xs font-bold shadow-lg border-2"
             [ngClass]="getAgeClass()">
          {{ ageRating }}
        </div>
      </div>

      <!-- Info bulle au survol -->
      <div class="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-10">
        {{ getScoreLabel() }}
        <div class="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: inline-block;
    }
  `]
})
export class ScoreBadgeComponent {
  @Input() score: number = 0;
  @Input() ageRating: string = '';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';

  getBgClass(): string {
    if (this.score >= 90) return 'bg-green-500';
    if (this.score >= 70) return 'bg-lime-500';
    if (this.score >= 50) return 'bg-yellow-500';
    if (this.score >= 30) return 'bg-orange-500';
    return 'bg-red-500';
  }

  getAgeClass(): string {
    switch(this.ageRating) {
      case '0+': return 'border-green-500 text-green-700';
      case '3+': return 'border-blue-500 text-blue-700';
      case '6+': return 'border-yellow-500 text-yellow-700';
      case '10+': return 'border-orange-500 text-orange-700';
      case '14+': return 'border-red-500 text-red-700';
      default: return 'border-gray-500 text-gray-700';
    }
  }

  getScoreLabel(): string {
    if (this.score >= 90) return 'Très calme - Parfait pour les tout-petits';
    if (this.score >= 70) return 'Calme - Bon rythme adapté';
    if (this.score >= 50) return 'Modéré - À surveiller';
    if (this.score >= 30) return 'Stimulant - Attention au rythme';
    return 'Très stimulant - Peut être trop intense';
  }
}