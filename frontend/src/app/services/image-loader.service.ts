import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ImageLoaderService {
  private cache = new Map<string, string>();
  private loadingImages = new Map<string, BehaviorSubject<boolean>>();

  preloadImage(url: string): Observable<boolean> {
    // Return cached status if already loading
    if (this.loadingImages.has(url)) {
      return this.loadingImages.get(url)!.asObservable();
    }

    // Create new loading subject
    const loading = new BehaviorSubject<boolean>(true);
    this.loadingImages.set(url, loading);

    // Start loading
    const img = new Image();
    
    img.onload = () => {
      this.cache.set(url, url);
      loading.next(false);
      loading.complete();
      this.loadingImages.delete(url);
    };

    img.onerror = () => {
      this.cache.set(url, '/assets/images/no-poster.svg');
      loading.next(false);
      loading.complete();
      this.loadingImages.delete(url);
    };

    img.src = url;
    return loading.asObservable();
  }

  getImageUrl(path: string, type: 'poster' | 'backdrop' = 'poster'): string {
    if (!path) {
      return type === 'poster' 
        ? '/assets/images/no-poster.svg'
        : '/assets/images/no-backdrop.svg';
    }

    const size = type === 'poster' ? 'w342' : 'w780';
    const url = `https://image.tmdb.org/t/p/${size}${path}`;

    return this.cache.get(url) || url;
  }

  clearCache(): void {
    this.cache.clear();
    this.loadingImages.clear();
  }
}