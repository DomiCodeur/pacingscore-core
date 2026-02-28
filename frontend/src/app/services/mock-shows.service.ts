import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';

export interface Show {
  id: number;
  title: string;
  poster_path: string;
  backdrop_path: string;
  composite_score: number;
  average_shot_length: number;
  num_scenes: number;
  evaluation_label: string;
  evaluation_description: string;
  evaluation_color: 'green' | 'lime' | 'yellow' | 'red';
  age_recommendation: string;
  description: string;
  analysis_details: {
    cuts_per_minute: number;
    flashs_detected: number;
    motion_intensity: number;
  };
}

@Injectable({
  providedIn: 'root'
})
export class MockShowsService {
  
  // Données en dur - 6 dessins animés avec vraies informations
  private readonly mockShows: Show[] = [
    {
      id: 1,
      title: "Puffin Rock",
      poster_path: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect width='300' height='450' fill='%234CAF50'/%3E%3Ctext x='150' y='180' font-family='Arial' font-size='32' fill='white' text-anchor='middle' font-weight='bold'%3EPuffin%3C/text%3E%3Ctext x='150' y='220' font-family='Arial' font-size='32' fill='white' text-anchor='middle' font-weight='bold'%3ERock%3C/text%3E%3Ctext x='150' y='320' font-family='Arial' font-size='24' fill='white' text-anchor='middle' font-weight='bold'%3E78/100%3C/text%3E%3Ctext x='150' y='360' font-family='Arial' font-size='16' fill='white' opacity='0.7' text-anchor='middle'%3E0-3 ans%3C/text%3E%3Ctext x='150' y='70' font-family='Arial' font-size='30' text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E",
      backdrop_path: "",
      composite_score: 78,
      average_shot_length: 12.5,
      num_scenes: 45,
      evaluation_label: "EXCELLENT",
      evaluation_description: "Rythme contemplatif, idéal pour les tout-petits.",
      evaluation_color: "green",
      age_recommendation: "0-3 ans",
      description: "Une série douce sur la vie d'un puffin sur une île irlandaise.",
      analysis_details: {
        cuts_per_minute: 4.8,
        flashs_detected: 0,
        motion_intensity: 12
      }
    },
    {
      id: 2,
      title: "Bluey",
      poster_path: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect width='300' height='450' fill='%238BC34A'/%3E%3Ctext x='150' y='200' font-family='Arial' font-size='36' fill='white' text-anchor='middle' font-weight='bold'%3EBluey%3C/text%3E%3Ctext x='150' y='320' font-family='Arial' font-size='24' fill='white' text-anchor='middle' font-weight='bold'%3E65/100%3C/text%3E%3Ctext x='150' y='360' font-family='Arial' font-size='16' fill='white' opacity='0.7' text-anchor='middle'%3E3-5 ans%3C/text%3E%3Ctext x='150' y='70' font-family='Arial' font-size='30' text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E",
      backdrop_path: "",
      composite_score: 65,
      average_shot_length: 9.2,
      num_scenes: 38,
      evaluation_label: "BON",
      evaluation_description: "Bon rythme pour les jeunes enfants.",
      evaluation_color: "lime",
      age_recommendation: "3-5 ans",
      description: "Une famille de chiens qui vit des aventures quotidiennes.",
      analysis_details: {
        cuts_per_minute: 6.5,
        flashs_detected: 1,
        motion_intensity: 25
      }
    },
    {
      id: 3,
      title: "Peppa Pig",
      poster_path: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect width='300' height='450' fill='%23FF9800'/%3E%3Ctext x='150' y='180' font-family='Arial' font-size='32' fill='white' text-anchor='middle' font-weight='bold'%3EPeppa%3C/text%3E%3Ctext x='150' y='220' font-family='Arial' font-size='32' fill='white' text-anchor='middle' font-weight='bold'%3EPig%3C/text%3E%3Ctext x='150' y='320' font-family='Arial' font-size='24' fill='white' text-anchor='middle' font-weight='bold'%3E55/100%3C/text%3E%3Ctext x='150' y='360' font-family='Arial' font-size='16' fill='white' opacity='0.7' text-anchor='middle'%3E5-7 ans%3C/text%3E%3Ctext x='150' y='70' font-family='Arial' font-size='30' text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E",
      backdrop_path: "",
      composite_score: 55,
      average_shot_length: 7.8,
      num_scenes: 42,
      evaluation_label: "MODÉRÉ",
      evaluation_description: "Rythme standard, OK pour enfants plus grands.",
      evaluation_color: "yellow",
      age_recommendation: "5-7 ans",
      description: "Une petite cochon qui vit des aventures avec sa famille.",
      analysis_details: {
        cuts_per_minute: 7.7,
        flashs_detected: 2,
        motion_intensity: 35
      }
    },
    {
      id: 4,
      title: "Cocomelon",
      poster_path: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect width='300' height='450' fill='%23F44336'/%3E%3Ctext x='150' y='180' font-family='Arial' font-size='28' fill='white' text-anchor='middle' font-weight='bold'%3ECocomelon%3C/text%3E%3Ctext x='150' y='320' font-family='Arial' font-size='24' fill='white' text-anchor='middle' font-weight='bold'%3E22/100%3C/text%3E%3Ctext x='150' y='360' font-family='Arial' font-size='16' fill='white' opacity='0.7' text-anchor='middle'%3E7+ ans%3C/text%3E%3Ctext x='150' y='70' font-family='Arial' font-size='30' text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E",
      backdrop_path: "",
      composite_score: 22,
      average_shot_length: 4.2,
      num_scenes: 85,
      evaluation_label: "RAPIDE",
      evaluation_description: "Attention : montage nerveux, risque de surstimulation.",
      evaluation_color: "red",
      age_recommendation: "7+ ans",
      description: "Vidéos musicales pour enfants avec montage rapide.",
      analysis_details: {
        cuts_per_minute: 14.3,
        flashs_detected: 8,
        motion_intensity: 75
      }
    },
    {
      id: 5,
      title: "Paw Patrol",
      poster_path: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect width='300' height='450' fill='%23FF9800'/%3E%3Ctext x='150' y='180' font-family='Arial' font-size='30' fill='white' text-anchor='middle' font-weight='bold'%3EPaw%3C/text%3E%3Ctext x='150' y='220' font-family='Arial' font-size='30' fill='white' text-anchor='middle' font-weight='bold'%3EPatrol%3C/text%3E%3Ctext x='150' y='320' font-family='Arial' font-size='24' fill='white' text-anchor='middle' font-weight='bold'%3E48/100%3C/text%3E%3Ctext x='150' y='360' font-family='Arial' font-size='16' fill='white' opacity='0.7' text-anchor='middle'%3E5-7 ans%3C/text%3E%3Ctext x='150' y='70' font-family='Arial' font-size='30' text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E",
      backdrop_path: "",
      composite_score: 48,
      average_shot_length: 6.5,
      num_scenes: 52,
      evaluation_label: "MODÉRÉ",
      evaluation_description: "Rythme d'action, peut être stimulant.",
      evaluation_color: "yellow",
      age_recommendation: "5-7 ans",
      description: "Une équipe de chiens qui sauvent les gens en difficulté.",
      analysis_details: {
        cuts_per_minute: 9.2,
        flashs_detected: 3,
        motion_intensity: 55
      }
    },
    {
      id: 6,
      title: "Tchoupi",
      poster_path: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450' viewBox='0 0 300 450'%3E%3Crect width='300' height='450' fill='%238BC34A'/%3E%3Ctext x='150' y='200' font-family='Arial' font-size='34' fill='white' text-anchor='middle' font-weight='bold'%3ETchoupi%3C/text%3E%3Ctext x='150' y='320' font-family='Arial' font-size='24' fill='white' text-anchor='middle' font-weight='bold'%3E72/100%3C/text%3E%3Ctext x='150' y='360' font-family='Arial' font-size='16' fill='white' opacity='0.7' text-anchor='middle'%3E0-3 ans%3C/text%3E%3Ctext x='150' y='70' font-family='Arial' font-size='30' text-anchor='middle'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E",
      backdrop_path: "",
      composite_score: 72,
      average_shot_length: 10.8,
      num_scenes: 35,
      evaluation_label: "BON",
      evaluation_description: "Rythme doux et adapté aux tout-petits.",
      evaluation_color: "lime",
      age_recommendation: "0-3 ans",
      description: "Un petit pingouin qui explore le monde qui l'entoure.",
      analysis_details: {
        cuts_per_minute: 5.6,
        flashs_detected: 0,
        motion_intensity: 15
      }
    }
  ];

  constructor() {}

  /**
   * Récupérer tous les dessins animés
   */
  getAllShows(): Observable<Show[]> {
    // Simule un délai réseau
    return of(this.mockShows).pipe(delay(300));
  }

  /**
   * Rechercher des dessins animés par titre
   */
  searchShows(query: string): Observable<Show[]> {
    const filtered = this.mockShows.filter(show => 
      show.title.toLowerCase().includes(query.toLowerCase())
    );
    return of(filtered).pipe(delay(200));
  }

  /**
   * Filtrer par score
   */
  filterByScore(minScore: number, maxScore?: number): Observable<Show[]> {
    let filtered = this.mockShows.filter(show => show.composite_score >= minScore);
    if (maxScore) {
      filtered = filtered.filter(show => show.composite_score <= maxScore);
    }
    return of(filtered).pipe(delay(200));
  }

  /**
   * Filtrer par âge recommandé
   */
  filterByAge(age: string): Observable<Show[]> {
    const filtered = this.mockShows.filter(show => 
      show.age_recommendation === age
    );
    return of(filtered).pipe(delay(200));
  }

  /**
   * Récupérer un dessin animé par ID
   */
  getShowById(id: number): Observable<Show | undefined> {
    const show = this.mockShows.find(s => s.id === id);
    return of(show).pipe(delay(200));
  }

  /**
   * Récupérer les scores de couleurs
   */
  getScoreColor(score: number): { bg: string; class: string; label: string } {
    if (score >= 80) return { bg: '#4caf50', class: 'green', label: 'Excellent' };
    if (score >= 60) return { bg: '#8bc34a', class: 'lime', label: 'Bon' };
    if (score >= 40) return { bg: '#ff9800', class: 'yellow', label: 'Modéré' };
    if (score >= 20) return { bg: '#f44336', class: 'red', label: 'Rapide' };
    return { bg: '#d32f2f', class: 'red', label: 'Trop rapide' };
  }
}