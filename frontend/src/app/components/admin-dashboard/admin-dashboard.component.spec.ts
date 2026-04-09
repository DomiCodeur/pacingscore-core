import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AdminDashboardComponent } from './admin-dashboard.component';
import { AnalysisService } from '../../services/analysis.service';
import { SupabaseAuthService } from '../../services/supabase-auth.service';
import { of } from 'rxjs';
import { HttpClientTestingModule } from '@angular/common/http/testing';

describe('AdminDashboardComponent', () => {
  let component: AdminDashboardComponent;
  let fixture: ComponentFixture<AdminDashboardComponent>;
  let mockAnalysisService: any;
  let mockAuthService: any;

  beforeEach(async () => {
    mockAnalysisService = {
      getFailedTasks: jest.fn().mockReturnValue(of([])),
      retryTask: jest.fn()
    };
    mockAuthService = {
      email$: of('admin@mollo.fr'),
      signOut: jest.fn().mockResolvedValue(null)
    };

    await TestBed.configureTestingModule({
      imports: [AdminDashboardComponent, HttpClientTestingModule],
      providers: [
        { provide: AnalysisService, useValue: mockAnalysisService },
        { provide: SupabaseAuthService, useValue: mockAuthService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(AdminDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('devrait charger les tâches échouées au démarrage', () => {
    expect(mockAnalysisService.getFailedTasks).toHaveBeenCalled();
  });

  it('devrait afficher l\'email de l\'utilisateur via le signal', () => {
    expect(component.userEmail()).toBe('admin@mollo.fr');
  });
});