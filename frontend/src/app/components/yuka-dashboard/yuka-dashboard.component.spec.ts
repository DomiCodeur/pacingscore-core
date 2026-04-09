import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { YukaDashboardComponent } from './yuka-dashboard.component';
import { SpringBootService } from '../../services/spring-boot.service';
import { of } from 'rxjs';

describe('YukaDashboardComponent', () => {
  let component: YukaDashboardComponent;
  let fixture: ComponentFixture<YukaDashboardComponent>;
  let mockService: any;

  beforeEach(async () => {
    mockService = {
      getVerifiedShowsCount: () => of({ count: 10 }),
      getAllShowsPaginated: () => of([])
    };

    await TestBed.configureTestingModule({
      imports: [YukaDashboardComponent, HttpClientTestingModule],
      providers: [{ provide: SpringBootService, useValue: mockService }]
    }).compileComponents();

    fixture = TestBed.createComponent(YukaDashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('devrait être créé', () => {
    expect(component).toBeTruthy();
  });

  it('devrait initialiser le nombre total de shows', () => {
    expect(component.totalShows()).toBe(10);
  });
});