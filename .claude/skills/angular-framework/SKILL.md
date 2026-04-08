---
name: angular-framework
description: Angular 18+, signals, standalone components, RxJS, Angular Router, HTTP client, NgRx
---

# Angular 18+ Framework

Modern Angular development: signals-based reactivity, standalone components, RxJS operators, typed HTTP client, Angular Router with guards, and NgRx state management.

## Standalone Component Architecture

Angular 18+ uses standalone components by default. No `NgModule` required:

```typescript
// main.ts
import { bootstrapApplication } from '@angular/platform-browser'
import { provideRouter, withComponentInputBinding, withViewTransitions } from '@angular/router'
import { provideHttpClient, withInterceptors } from '@angular/common/http'
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async'
import { APP_ROUTES } from './app/app.routes'
import { authInterceptor } from './app/core/interceptors/auth.interceptor'
import { AppComponent } from './app/app.component'

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(APP_ROUTES,
      withComponentInputBinding(),    // route params as @Input
      withViewTransitions()
    ),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimationsAsync(),
  ],
})
```

## Signals-Based Components (Angular 18)

```typescript
// user-list.component.ts
import {
  Component, OnInit, inject, signal, computed, effect, linkedSignal
} from '@angular/core'
import { toSignal } from '@angular/core/rxjs-interop'
import { FormsModule } from '@angular/forms'
import { RouterLink } from '@angular/router'
import { UserService } from '../services/user.service'
import { User } from '../models/user.model'

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [FormsModule, RouterLink, UserCardComponent],
  template: `
    <div class="container">
      <h1>Users ({{ filteredUsers().length }})</h1>

      <input
        [(ngModel)]="searchQuery"
        placeholder="Search users..."
        class="search-input"
      />

      @if (isLoading()) {
        <div class="loading-spinner" />
      } @else if (error()) {
        <div class="error-banner">{{ error() }}</div>
      } @else {
        <div class="user-grid">
          @for (user of filteredUsers(); track user.id) {
            <app-user-card
              [user]="user"
              (deleted)="onUserDeleted($event)"
            />
          } @empty {
            <p>No users found.</p>
          }
        </div>
      }
    </div>
  `,
})
export class UserListComponent implements OnInit {
  private userService = inject(UserService)

  // Writable signals
  searchQuery = signal('')
  isLoading = signal(false)
  error = signal<string | null>(null)
  users = signal<User[]>([])

  // Computed signal — automatically tracks dependencies
  filteredUsers = computed(() => {
    const query = this.searchQuery().toLowerCase()
    if (!query) return this.users()
    return this.users().filter(u =>
      u.name.toLowerCase().includes(query) ||
      u.email.toLowerCase().includes(query)
    )
  })

  // Effect — runs when signal changes
  private searchEffect = effect(() => {
    console.log(`Searching for: ${this.searchQuery()}`)
  })

  async ngOnInit() {
    this.isLoading.set(true)
    this.error.set(null)
    try {
      const users = await this.userService.getAll()
      this.users.set(users)
    } catch (e: any) {
      this.error.set(e.message)
    } finally {
      this.isLoading.set(false)
    }
  }

  onUserDeleted(id: string) {
    this.users.update(users => users.filter(u => u.id !== id))
  }
}
```

## Typed HTTP Client

```typescript
// user.service.ts
import { Injectable, inject } from '@angular/core'
import { HttpClient, HttpParams } from '@angular/common/http'
import { Observable, throwError } from 'rxjs'
import { catchError, map, tap } from 'rxjs/operators'
import { environment } from '../../environments/environment'
import { User, CreateUserDto, UpdateUserDto, PaginatedResult } from '../models'

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient)
  private readonly baseUrl = `${environment.apiUrl}/users`

  getAll(params?: {
    page?: number
    pageSize?: number
    search?: string
  }): Observable<PaginatedResult<User>> {
    let httpParams = new HttpParams()
    if (params?.page != null) httpParams = httpParams.set('page', params.page)
    if (params?.pageSize != null) httpParams = httpParams.set('page_size', params.pageSize)
    if (params?.search) httpParams = httpParams.set('q', params.search)

    return this.http.get<PaginatedResult<User>>(this.baseUrl, { params: httpParams }).pipe(
      tap(result => console.log(`Fetched ${result.data.length} users`)),
      catchError(this.handleError)
    )
  }

  getById(id: string): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/${id}`).pipe(
      catchError(this.handleError)
    )
  }

  create(dto: CreateUserDto): Observable<User> {
    return this.http.post<User>(this.baseUrl, dto).pipe(
      catchError(this.handleError)
    )
  }

  update(id: string, dto: UpdateUserDto): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/${id}`, dto).pipe(
      catchError(this.handleError)
    )
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`).pipe(
      catchError(this.handleError)
    )
  }

  private handleError(error: any): Observable<never> {
    const message = error.error?.message || error.message || 'An error occurred'
    console.error('API Error:', error)
    return throwError(() => new Error(message))
  }
}

// Functional HTTP interceptor (Angular 15+)
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService)
  const token = authService.getToken()

  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    })
  }

  return next(req).pipe(
    catchError(error => {
      if (error.status === 401) {
        authService.logout()
      }
      return throwError(() => error)
    })
  )
}
```

## Angular Router with Guards

```typescript
// app.routes.ts
import { Routes } from '@angular/router'
import { authGuard } from './core/guards/auth.guard'
import { roleGuard } from './core/guards/role.guard'

export const APP_ROUTES: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard],
  },
  {
    path: 'users',
    loadChildren: () => import('./features/users/users.routes').then(m => m.USERS_ROUTES),
    canActivate: [authGuard],
    canActivateChild: [roleGuard('admin')],
  },
  {
    path: '**',
    loadComponent: () => import('./shared/components/not-found.component').then(m => m.NotFoundComponent),
  },
]

// Functional auth guard
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService)
  const router = inject(Router)

  if (authService.isAuthenticated()) return true

  return router.createUrlTree(['/auth/login'], {
    queryParams: { returnUrl: state.url }
  })
}

// Role guard factory
export const roleGuard = (requiredRole: string): CanActivateChildFn =>
  (childRoute, state) => {
    const authService = inject(AuthService)
    if (authService.hasRole(requiredRole)) return true
    return inject(Router).createUrlTree(['/forbidden'])
  }
```

## NgRx with Signals Store

```typescript
// users.store.ts (NgRx Signals Store — v18)
import { signalStore, withState, withComputed, withMethods, patchState } from '@ngrx/signals'
import { rxMethod } from '@ngrx/signals/rxjs-interop'
import { tapResponse } from '@ngrx/operators'
import { computed, inject } from '@angular/core'
import { pipe, switchMap, debounceTime, distinctUntilChanged } from 'rxjs'

interface UsersState {
  users: User[]
  selectedUser: User | null
  isLoading: boolean
  error: string | null
  searchQuery: string
  currentPage: number
  totalItems: number
}

const initialState: UsersState = {
  users: [],
  selectedUser: null,
  isLoading: false,
  error: null,
  searchQuery: '',
  currentPage: 1,
  totalItems: 0,
}

export const UsersStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),

  withComputed(({ users, searchQuery }) => ({
    filteredUsers: computed(() => {
      const q = searchQuery().toLowerCase()
      return q ? users().filter(u => u.name.toLowerCase().includes(q)) : users()
    }),
    hasUsers: computed(() => users().length > 0),
  })),

  withMethods((store, userService = inject(UserService)) => ({
    loadUsers: rxMethod<{ page: number; search?: string }>(
      pipe(
        tap(() => patchState(store, { isLoading: true, error: null })),
        switchMap(({ page, search }) =>
          userService.getAll({ page, search }).pipe(
            tapResponse({
              next: (result) => patchState(store, {
                users: result.data,
                totalItems: result.total,
                isLoading: false,
              }),
              error: (err: Error) => patchState(store, {
                error: err.message,
                isLoading: false,
              }),
            })
          )
        )
      )
    ),

    selectUser(user: User | null) {
      patchState(store, { selectedUser: user })
    },

    setSearchQuery: rxMethod<string>(
      pipe(
        debounceTime(300),
        distinctUntilChanged(),
        tap(query => patchState(store, { searchQuery: query, currentPage: 1 }))
      )
    ),
  }))
)
```

## RxJS Patterns

```typescript
// Complex reactive pattern: autocomplete with cancellation
@Component({ /* ... */ })
export class SearchComponent {
  private searchSubject = new Subject<string>()
  results$: Observable<SearchResult[]>

  constructor(private searchService: SearchService) {
    this.results$ = this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      filter(q => q.length >= 2),
      switchMap(query =>              // cancels previous request
        this.searchService.search(query).pipe(
          catchError(() => of([]))    // graceful fallback
        )
      ),
      shareReplay(1)                  // share with multiple subscribers
    )
  }

  onSearchChange(query: string) {
    this.searchSubject.next(query)
  }
}

// Converting signal to Observable and back
const users$ = toObservable(usersSignal)          // signal → Observable
const usersFromObs = toSignal(users$, { initialValue: [] }) // Observable → signal
```

## Best Practices

- Use signals for local component state; NgRx Signals Store for shared state
- Prefer `@if` / `@for` / `@switch` (control flow) over `*ngIf` / `*ngFor` — they're type-safe and tree-shakeable
- Use `withComponentInputBinding()` to bind route params as `@Input` signals
- Lazy-load all feature modules via `loadComponent` / `loadChildren` for smaller initial bundles
- Use functional guards and interceptors (arrow functions) over class-based
- Enable `strictTemplates: true` in `tsconfig.json` for full template type checking
- Use `OnPush` change detection strategy on all components for performance
- Avoid subscribing in components — use `async` pipe or `toSignal` instead
- Unsubscribe with `takeUntilDestroyed(this.destroyRef)` — no manual unsubscribe needed
- Use `@defer` blocks for progressive loading of heavy components

## Models to Use

- **Default**: `claude-sonnet-4-5` — signals, RxJS, routing, HTTP client
- **Architecture**: `claude-opus-4-5` — NgRx design, complex reactive flows, multi-module
- **Quick snippets**: `claude-haiku-3-5` — simple components, pipes, utility functions
