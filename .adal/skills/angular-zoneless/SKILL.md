---
name: angular-zoneless
description: "ALWAYS use when working with Angular Zoneless, zoneless change detection, provideZonelessChangeDetection, or removing zone.js in Angular applications."
metadata:
  version: 21.0.0
  generated_by: oguzhancart
  generated_at: 2026-02-19
---

# Angular Zoneless

**Version:** Angular 19+ (2025)
**Tags:** Zoneless, Change Detection, Signals, Reactivity

**References:** [Zoneless Guide](https://angular.dev/guide/experimental/zoneless) • [Signals](https://angular.dev/guide/signals)

## API Changes

This section documents recent version-specific API changes.

- NEW: provideZonelessChangeDetection — Enable zoneless mode [source](https://angular.dev/guide/experimental/zoneless)

- NEW: afterNextRender — Run code after rendering without zone.js

- NEW: Experimental Zoneless — Available since Angular 17, stable in Angular 19+

- NEW: signal() + computed() — Works without zone.js

## Best Practices

- Enable zoneless change detection

```ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection()
  ]
};
```

- Use signals for reactivity

```ts
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>Count: {{ count() }}</p>
    <p>Double: {{ double() }}</p>
  `
})
export class CounterComponent {
  count = signal(0);
  double = computed(() => this.count() * 2);

  increment() {
    this.count.update(c => c + 1);
  }
}
```

- Use afterNextRender for DOM operations

```ts
constructor() {
  afterNextRender(() => {
    // Runs after rendering, outside zone
    this.initChart();
  });
}
```

- Use afterRender for repeated operations

```ts
constructor() {
  afterRender(() => {
    // Runs after every render
  });
}
```

- Handle async without zone.js

```ts
@Component({
  template: `
    @if (data$ | async; as data) {
      {{ data.name }}
    }
  `
})
export class AsyncComponent {
  data$ = from(fetch('/api/data')).pipe(
    share()
  );
}
```

- Use ChangeDetectorRef manually when needed

```ts
constructor(private cdr: ChangeDetectorRef) {}

update() {
  this.value = newValue;
  this.cdr.markForCheck();
}
```

- Remove zone.js from polyfills

```ts
// polyfills.ts
// Remove or comment out zone.js import
// import 'zone.js';
```

- Use untracked for non-reactive reads

```ts
import { untracked } from '@angular/core';

ngOnInit() {
  // Read without creating dependency
  const value = untracked(() => this.signal());
}
```

- Handle browser events

```ts
@HostListener('click')
onClick() {
  // Works without zone.js
  this.count.update(c => c + 1);
}
```

- Test in zoneless mode

```ts
TestBed.configureTestingModule({
  providers: [
    provideZonelessChangeDetection()
  ]
});
```
