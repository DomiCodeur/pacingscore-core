import { Component, OnInit, inject, signal, computed, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { debounceTime, distinctUntilChanged } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { SpringBootService, Show } from '../../services/spring-boot.service';

@Component({
  selector: 'app-yuka-dashboard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './yuka-dashboard.component.html',
  styleUrl: './yuka-dashboard.component.css'
})
export class YukaDashboardComponent implements OnInit {
  private springBootService = inject(SpringBootService);

  // 🌟 État géré par des Signals
  shows = signal<Show[]>([]);
  totalShows = signal(0);
  loading = signal(false);
  loadingMore = signal(false);
  hasMore = signal(true);
  selectedShow = signal<Show | null>(null);

  // 🌟 Signaux de filtrage
  activeFilter = signal('all');
  activeAgeFilter = signal('all');
  activeTypeFilter = signal('all');
  activeDevelopmentalAgeFilter = signal('all');

  searchControl = new FormControl('');
  searchTerm = toSignal(this.searchControl.valueChanges.pipe(
    debounceTime(400),
    distinctUntilChanged()
  ), { initialValue: '' });

  // 🌟 Logic Déclarative : Recalcul automatique et performant
  filteredShows = computed(() => {
    let results = this.shows();
    const term = this.searchTerm()?.toLowerCase();
    
    if (term) {
      results = results.filter(s => s.title.toLowerCase().includes(term));
    }

    // Filtrage par rythme
    const pacing = this.activeFilter();
    if (pacing === 'excellent') results = results.filter(s => s.composite_score >= 80);
    else if (pacing === 'good') results = results.filter(s => s.composite_score >= 60 && s.composite_score < 80);
    else if (pacing === 'moderate') results = results.filter(s => s.composite_score >= 40 && s.composite_score < 60);
    else if (pacing === 'fast') results = results.filter(s => s.composite_score < 40);

    // Filtrage par âge et type
    if (this.activeAgeFilter() !== 'all') {
      results = results.filter(s => s.age_recommendation === this.activeAgeFilter());
    }
    if (this.activeTypeFilter() !== 'all') {
      results = results.filter(s => s.media_type === this.activeTypeFilter());
    }

    return results;
  });

  averageScore = computed(() => {
    const s = this.shows();
    return s.length ? s.reduce((sum, item) => sum + item.composite_score, 0) / s.length : 0;
  });

  ngOnInit() {
    this.springBootService.getVerifiedShowsCount().subscribe(res => this.totalShows.set(res.count));
    this.loadPage(0);
  }

  loadPage(page: number) {
    if (page === 0) this.loading.set(true);
    else this.loadingMore.set(true);

    this.springBootService.getAllShowsPaginated(50, page * 50, 'all', 0, undefined, undefined, true)
      .subscribe({
        next: (newShows) => {
          this.shows.update(current => page === 0 ? newShows : [...current, ...newShows]);
          this.hasMore.set(newShows.length >= 50);
          this.loading.set(false);
          this.loadingMore.set(false);
        }
      });
  }

  @HostListener('window:scroll', [])
  onScroll() {
    const pos = (document.documentElement.scrollTop || document.body.scrollTop) + document.documentElement.offsetHeight;
    const max = document.documentElement.scrollHeight;
    if (pos >= max - 200 && !this.loadingMore() && this.hasMore()) {
      this.loadPage(Math.floor(this.shows().length / 50));
    }
  }

  getScoreBg = (score: number) => score >= 80 ? '#22c55e' : score >= 60 ? '#84cc16' : score >= 40 ? '#f59e0b' : '#ef4444';
}