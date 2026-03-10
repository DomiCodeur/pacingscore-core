import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { YukaDashboardComponent } from './components/yuka-dashboard/yuka-dashboard.component';
import { AdminDashboardComponent } from './components/admin-dashboard/admin-dashboard.component';
import { AuthLoginComponent } from './auth-login.component';
import { SpringBootService } from './services/spring-boot.service';
import { AnalysisService } from './services/analysis.service';
import { SupabaseAuthService } from './services/supabase-auth.service';
import { AppRoutingModule } from './app-routing.module';

@NgModule({
  declarations: [
    AppComponent,
    YukaDashboardComponent,
    AdminDashboardComponent,
    AuthLoginComponent
  ],
  imports: [
    BrowserModule,
    ReactiveFormsModule,
    FormsModule,
    HttpClientModule,
    AppRoutingModule
  ],
  providers: [
    SpringBootService,
    AnalysisService,
    SupabaseAuthService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }