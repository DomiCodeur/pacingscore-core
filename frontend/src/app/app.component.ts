import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="min-h-screen bg-gray-50">
      <!-- Navigation -->
      <nav class="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center gap-8">
              <a href="#" class="flex items-center gap-3 text-decoration-none">
                <div class="w-10 h-10 bg-green-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                  🎬
                </div>
                <div>
                  <h1 class="text-base font-bold text-gray-900 leading-tight">Mollo</h1>
                  <p class="text-[10px] text-gray-500 font-medium">Le score des dessins animés</p>
                </div>
              </a>
              <div class="flex items-center gap-4">
                <a 
                  routerLink="/home" 
                  routerLinkActive="bg-green-100 text-green-700" 
                  class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  Dashboard
                </a>
                <a 
                  routerLink="/admin" 
                  routerLinkActive="bg-blue-100 text-blue-700"
                  class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  Admin
                </a>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <!-- Main Content -->
      <main class="pb-10">
        <router-outlet></router-outlet>
      </main>
    </div>
  `
})
export class AppComponent {
  title = 'Mollo - Le Yuka des Dessins Animés';
}