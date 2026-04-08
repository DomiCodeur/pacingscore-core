import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ScoreBadgeComponent } from './score-badge.component';

describe('ScoreBadgeComponent', () => {
  let component: ScoreBadgeComponent;
  let fixture: ComponentFixture<ScoreBadgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScoreBadgeComponent] // On importe le composant Standalone
    }).compileComponents();

    fixture = TestBed.createComponent(ScoreBadgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('devrait créer le composant', () => {
    expect(component).toBeTruthy();
  });

  it('devrait calculer la bonne couleur de fond (bgClass) selon le score', () => {
    // On simule l'entrée d'un score à 95%
    fixture.componentRef.setInput('score', 95);
    fixture.detectChanges();
    expect(component.bgClass()).toBe('bg-green-500');

    // On simule un score à 40%
    fixture.componentRef.setInput('score', 40);
    fixture.detectChanges();
    expect(component.bgClass()).toBe('bg-orange-500');
  });
});