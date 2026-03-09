import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { YukaDashboardComponent } from './components/yuka-dashboard/yuka-dashboard.component';
import { AdminDashboardComponent } from './components/admin-dashboard/admin-dashboard.component';

const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: YukaDashboardComponent },
  { path: 'admin', component: AdminDashboardComponent },
  // Wildcard route: redirect to home
  { path: '**', redirectTo: '/home' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { scrollPositionRestoration: 'enabled' })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
