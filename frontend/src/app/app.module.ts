import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { YukaDashboardComponent } from './components/yuka-dashboard/yuka-dashboard.component';
import { SpringBootService } from './services/spring-boot.service';

@NgModule({
  declarations: [
    AppComponent,
    YukaDashboardComponent
  ],
  imports: [
    BrowserModule,
    ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [
    SpringBootService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }