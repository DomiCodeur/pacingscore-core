import { Component, inject, computed } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { SupabaseAuthService } from './services/supabase-auth.service';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive], 
  template: `
    <div class="min-h-screen bg-gray-50">
      <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            
            <a routerLink="/" class="flex items-center gap-3 no-underline">
              <div class="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                🎬
              </div>
              <div class="hidden sm:block"> <h1 class="text-base font-bold text-gray-900 leading-tight">Mollo</h1>
                <p class="text-[10px] text-gray-500 font-medium">Le score des dessins animés</p>
              </div>
            </a>
            
            <div class="flex items-center gap-2 sm:gap-4">
              <a routerLink="/home" 
                 routerLinkActive="bg-green-100 text-green-700" 
                 class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                Dashboard
              </a>

              @if (isAdmin()) {
                <a routerLink="/admin" 
                   routerLinkActive="bg-blue-100 text-blue-700"
                   class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  Admin
                </a>
              }

              @if (!isLoggedIn()) {
                <a routerLink="/login"
                   class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  Connexion
                </a>
              } @else {
                <button (click)="signOut()" 
                        class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  Déconnexion
                </button>
              }
            </div>

          </div>
        </div>
      </nav>

      <main>
        <router-outlet></router-outlet>
      </main>

      <footer class="bg-white border-t border-gray-100 py-10">
        <div class="max-w-7xl mx-auto px-4 text-center">
          <div class="text-gray-400 text-xs font-bold tracking-widest uppercase mb-2">Mollo Project</div>
          <p class="text-gray-400 text-[10px]">Utilise l'API TMDB pour les métadonnées et images.</p>
        </div>
      </footer>
      
    </div>
  `
})
export class AppComponent {
  private auth = inject(SupabaseAuthService);
  private router = inject(Router);

  title = 'Mollo - Le Yuka des Dessins Animés';

  // Conversion des Observables en Signals pour supprimer le pipe | async
  isAdmin = toSignal(this.auth.isAdmin$, { initialValue: false });
  isLoggedIn = toSignal(this.auth.user$.pipe(map(user => !!user)), { initialValue: false });

  async signOut(): Promise<void> {
    await this.auth.signOut();
    this.router.navigate(['/home']);
  }
}