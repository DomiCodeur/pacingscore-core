import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="min-h-screen bg-gray-50">
      <app-yuka-dashboard></app-yuka-dashboard>
    </div>
  `
})
export class AppComponent {
  title = 'Mollo - Le Yuka des Dessins Animés';
}