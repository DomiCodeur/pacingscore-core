import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <app-show-grid></app-show-grid>
    </div>
  `
})
export class AppComponent {
  title = 'PacingScore Kids';
}