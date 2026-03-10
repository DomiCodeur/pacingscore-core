import { Injectable } from '@angular/core';
import { createClient, SupabaseClient, User } from '@supabase/supabase-js';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SupabaseAuthService {
  private supabase: SupabaseClient;
  private userSubject = new BehaviorSubject<User | null>(null);

  constructor() {
    this.supabase = createClient(environment.supabaseUrl, environment.supabaseAnonKey);
    this.initAuth();
  }

  private async initAuth() {
    const { data: { session } } = await this.supabase.auth.getSession();
    this.userSubject.next(session?.user ?? null);

    this.supabase.auth.onAuthStateChange((_event, session) => {
      this.userSubject.next(session?.user ?? null);
    });
  }

  get user$(): Observable<User | null> {
    return this.userSubject.asObservable();
  }

  get email$(): Observable<string | null> {
    return this.userSubject.pipe(map(user => user?.email ?? null));
  }

  get isAdmin$(): Observable<boolean> {
    const ADMIN_EMAIL = 'mathieu.domichard@gmail.com'; // whitelist email
    return this.userSubject.pipe(map(user => user?.email === ADMIN_EMAIL));
  }

  async signInWithEmail(email: string, password: string): Promise<{ error: any }> {
    const { error } = await this.supabase.auth.signInWithPassword({ email, password });
    return { error };
  }

  async signUp(email: string, password: string): Promise<{ error: any }> {
    const { error } = await this.supabase.auth.signUp({ email, password });
    return { error };
  }

  async signOut(): Promise<void> {
    await this.supabase.auth.signOut();
  }

  async getCurrentUser(): Promise<User | null> {
    const { data: { user } } = await this.supabase.auth.getUser();
    return user;
  }
}
