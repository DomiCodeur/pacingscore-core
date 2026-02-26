import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { ShowGridComponent } from './components/show-grid/show-grid.component';
import { ShowSearchComponent } from './components/show-search/show-search.component';
import { ShowCardComponent } from './components/show-card/show-card.component';
import { ScoreBadgeComponent } from './components/score-badge/score-badge.component';
import { AdminPanelComponent } from './components/admin-panel/admin-panel.component';
import { ShowService } from './services/show.service';
import { ImageLoaderService } from './services/image-loader.service';

@NgModule({
  declarations: [
    AppComponent,
    ShowGridComponent,
    ShowSearchComponent,
    ShowCardComponent,
    ScoreBadgeComponent,
    AdminPanelComponent
  ],
  imports: [
    BrowserModule,
    ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [
    ShowService,
    ImageLoaderService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }