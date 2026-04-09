import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // 🌟 Indispensable pour ngModel
import { AnalysisService, FailedTask } from '../../services/analysis.service';
import { SupabaseAuthService } from '../../services/supabase-auth.service';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule], // 🌟 On ajoute FormsModule ici
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.css'
})
export class AdminDashboardComponent implements OnInit {
  private analysisService = inject(AnalysisService);
  private auth = inject(SupabaseAuthService);

  // 🌟 État géré par des Signals
  failedTasks = signal<FailedTask[]>([]);
  loading = signal(false);
  retrying = signal<string | null>(null);
  
  // Conversion de l'observable email en Signal
  userEmail = toSignal(this.auth.email$, { initialValue: 'inconnu' });

  ngOnInit(): void {
    this.loadFailedTasks();
  }

  signOut(): void {
    this.auth.signOut().then(() => {
      window.location.href = '/home';
    });
  }

  loadFailedTasks(): void {
    this.loading.set(true);
    this.analysisService.getFailedTasks(100).subscribe({
      next: (tasks) => {
        // On initialise manualUrl et _removing pour chaque tâche
        this.failedTasks.set(tasks.map(t => ({ ...t, manualUrl: '', _removing: false })));
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Erreur chargement tâches', err);
        this.loading.set(false);
        this.failedTasks.set([]);
      }
    });
  }

  retryTask(task: FailedTask): void {
    this.retrying.set(task.id);
    const manualUrl = task.manualUrl?.trim() || undefined;

    this.analysisService.retryTask(task.id, manualUrl).subscribe({
      next: (result) => {
        if (result.success) {
          // Mise à jour visuelle : on marque comme supprimé
          this.failedTasks.update(tasks => 
            tasks.map(t => t.id === task.id ? { ...t, _removing: true } : t)
          );
          
          setTimeout(() => {
            this.failedTasks.update(tasks => tasks.filter(t => t.id !== task.id));
          }, 300);
        } else {
          alert('Erreur : ' + (result.error || 'Inconnu'));
        }
        this.retrying.set(null);
      },
      error: () => {
        alert('Erreur réseau');
        this.retrying.set(null);
      }
    });
  }
}