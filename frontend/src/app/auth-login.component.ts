import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { SupabaseAuthService } from './services/supabase-auth.service';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-auth-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div class="max-w-md w-full bg-white rounded-2xl shadow-lg p-8">
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-green-500 rounded-2xl flex items-center justify-center text-white text-3xl mx-auto mb-4">
            🎬
          </div>
          <h1 class="text-2xl font-bold text-gray-900">Connexion Mollo</h1>
          <p class="text-gray-500 mt-2">Accédez à votre compte admin</p>
        </div>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              formControlName="email"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition-all"
              placeholder="votre@email.com"
            />
            @if (loginForm.get('email')?.invalid && loginForm.get('email')?.touched) {
              <p class="text-red-500 text-sm mt-1">Email requis</p>
            }
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Mot de passe</label>
            <input
              type="password"
              formControlName="password"
              class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none transition-all"
              placeholder="••••••••"
            />
            @if (loginForm.get('password')?.invalid && loginForm.get('password')?.touched) {
              <p class="text-red-500 text-sm mt-1">Mot de passe requis</p>
            }
          </div>

          @if (errorMessage) {
            <div class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">
              {{ errorMessage }}
            </div>
          }

          <button
            type="submit"
            [disabled]="loginForm.invalid || loading"
            class="w-full py-3 bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white font-semibold rounded-xl transition-colors"
          >
            @if (loading) {
              <span class="animate-spin mr-2">⏳</span> Connexion...
            } @else {
              Se connecter
            }
          </button>
        </form>

        <div class="mt-6 text-center text-sm text-gray-500">
          <p>Utilisez l'email admin configuré dans Supabase Auth.</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host { display: block; }
  `]
})
export class AuthLoginComponent {
  loginForm: FormGroup;
  loading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private auth: SupabaseAuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.loading = true;
    this.errorMessage = '';

    const { email, password } = this.loginForm.value;

    this.auth.signInWithEmail(email, password).then(({ error }) => {
      this.loading = false;
      if (error) {
        this.errorMessage = error.message || 'Erreur de connexion';
      } else {
        this.router.navigate(['/admin']);
      }
    });
  }
}
