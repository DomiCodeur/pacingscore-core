import { Component, input, computed } from '@angular/core';

@Component({
  selector: 'app-score-badge',
  standalone: true,
  templateUrl: './score-badge.component.html',
  styleUrl: './score-badge.component.css'
})
export class ScoreBadgeComponent {
  // Déclaration des Inputs avec les Signals
  score = input<number>(0);
  ageRating = input<string>('');
  size = input<'sm' | 'md' | 'lg'>('md');

  // Valeurs calculées et mises en cache pour la performance
  bgClass = computed(() => {
    const s = this.score();
    if (s >= 90) return 'bg-green-500';
    if (s >= 70) return 'bg-lime-500';
    if (s >= 50) return 'bg-yellow-500';
    if (s >= 30) return 'bg-orange-500';
    return 'bg-red-500';
  });

  ageClass = computed(() => {
    switch(this.ageRating()) {
      case '0+': return 'border-green-500 text-green-700';
      case '3+': return 'border-blue-500 text-blue-700';
      case '6+': return 'border-yellow-500 text-yellow-700';
      case '10+': return 'border-orange-500 text-orange-700';
      case '14+': return 'border-red-500 text-red-700';
      default: return 'border-gray-500 text-gray-700';
    }
  });

  scoreLabel = computed(() => {
    const s = this.score();
    if (s >= 90) return 'Très calme - Parfait pour les tout-petits';
    if (s >= 70) return 'Calme - Bon rythme adapté';
    if (s >= 50) return 'Modéré - À surveiller';
    if (s >= 30) return 'Stimulant - Attention au rythme';
    return 'Très stimulant - Peut être trop intense';
  });
}