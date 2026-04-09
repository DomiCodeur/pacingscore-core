import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { map } from 'rxjs/operators';
import { SupabaseAuthService } from '../services/supabase-auth.service';

export const adminGuard: CanActivateFn = (route, state) => {
  const auth = inject(SupabaseAuthService);
  const router = inject(Router);

  return auth.isAdmin$.pipe(
    map(isAdmin => {
      if (isAdmin) {
        return true;
      }
      // Redirection vers home si non-admin
      return router.createUrlTree(['/home']);
    })
  );
};