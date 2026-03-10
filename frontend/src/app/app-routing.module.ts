import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { YukaDashboardComponent } from './components/yuka-dashboard/yuka-dashboard.component';
import { AdminDashboardComponent } from './components/admin-dashboard/admin-dashboard.component';
import { AuthLoginComponent } from './auth-login.component';
import { AdminGuard } from './guards/admin.guard';

const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: YukaDashboardComponent },
  { path: 'login', component: AuthLoginComponent },
  { path: 'admin', component: AdminDashboardComponent, canActivate: [AdminGuard] },
  // Wildcard route: redirect to home
  { path: '**', redirectTo: '/home' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { scrollPositionRestoration: 'enabled' })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
