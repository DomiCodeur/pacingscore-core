import { Routes } from '@angular/router';
import { adminGuard } from './guards/admin.guard'; // On passe en version fonctionnelle

export const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { 
    path: 'home', 
    loadComponent: () => import('./components/yuka-dashboard/yuka-dashboard.component')
      .then(m => m.YukaDashboardComponent) 
  },
  { 
    path: 'login', 
    loadComponent: () => import('./auth-login.component').then(m => m.AuthLoginComponent)
  },
  { 
    path: 'admin', 
    loadComponent: () => import('./components/admin-dashboard/admin-dashboard.component')
      .then(m => m.AdminDashboardComponent),
    canActivate: [adminGuard]
  },
  { path: '**', redirectTo: 'home' }
];