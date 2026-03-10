import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { SupabaseAuthService } from '../services/supabase-auth.service';

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {
  constructor(
    private auth: SupabaseAuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean | UrlTree> {
    return this.auth.isAdmin$.pipe(
      map(isAdmin => {
        if (isAdmin) {
          return true;
        }
        return this.router.createUrlTree(['/home']); // redirect non-admin to home
      })
    );
  }
}
