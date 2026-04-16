---
name: angular-ssr
description: "ALWAYS use when working with Angular SSR, server-side rendering, hydration, prerendering, or Angular Universal in Angular applications."
metadata:
  version: 21.0.0
  generated_by: oguzhancart
  generated_at: 2026-02-19
---

# @angular/ssr (Server-Side Rendering)

**Version:** Angular 21 (2025)
**Tags:** SSR, Hydration, Prerendering, SEO, Angular Universal

**References:** [SSR Guide](https://angular.io/guide/ssr) • [Hydration](https://angular.io/guide/hydration) • [@angular/ssr](https://angular.io/api/platform-server)

## API Changes

This section documents recent version-specific API changes.

- NEW: Incremental Hydration — Hydrate components incrementally instead of all at once [source](https://www.angulararchitects.io/blog/guide-for-ssr/)

- NEW: Hybrid Rendering — Per-route rendering mode configuration [source](https://fluin.io/blog/state-of-angular-ssr-2025)

- NEW: `provideClientHydration` — Modern hydration setup with event replay

- NEW: Deferrable views (@defer) — Load components lazily with SSR support

- NEW: `ngSkipHydration` — Opt-out of hydration for specific components

- DEPRECATED: Angular Universal — Migrate to @angular/ssr

## Best Practices

- Enable SSR with CLI

```bash
ng add @angular/ssr

# Or create new project with SSR
ng new my-app --ssr
```

- Enable client hydration

```ts
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration()
  ]
};
```

- Use incremental hydration for better performance

```ts
import { provideClientHydration, withIncrementalHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(withIncrementalHydration())
  ]
};
```

- Use @defer for lazy loading

```ts
@Component({
  template: `
    @defer (on viewport) {
      <heavy-component />
    } @placeholder {
      <div>Loading...</div>
    }
  `
})
export class MainComponent {}
```

- Handle browser-specific code with isPlatformBrowser

```ts
import { PLATFORM_ID, Inject } from '@angular/core';

constructor(@Inject(PLATFORM_ID) private platformId: Object) {
  if (isPlatformBrowser(this.platformId)) {
    // Browser-only code
  }
}
```

- Use TransferState to prevent duplicate HTTP requests

```ts
import { TransferState, makeStateKey } from '@angular/platform-browser';

@Injectable()
export class DataService {
  constructor(private http: HttpClient, private transferState: TransferState) {}

  getData() {
    const DATA_KEY = makeStateKey('DATA');
    
    if (this.transferState.hasKey(DATA_KEY)) {
      return of(this.transferState.get(DATA_KEY, []));
    }
    
    return this.http.get('/api/data').pipe(
      tap(data => this.transferState.set(DATA_KEY, data))
    );
  }
}
```

- Skip hydration for DOM-manipulating components

```ts
@Component({
  selector: 'app-third-party',
  host: {
    'ngSkipHydration': 'true'
  }
})
export class ThirdPartyComponent {}
```

- Configure hybrid rendering per route

```ts
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    path: 'dashboard',
    renderMode: RenderMode.Client
  },
  {
    path: 'blog/:slug',
    renderMode: RenderMode.Server
  },
  {
    path: 'about',
    renderMode: RenderMode.Prerender
  }
];
```

- Use platform-server for server-side logic

```ts
import { isPlatformServer } from '@angular/common';

constructor(@Inject(PLATFORM_ID) platformId: Object) {
  if (isPlatformServer(platformId)) {
    // Server-side only
  }
}
```
