---
name: angular-signals-http
description: "ALWAYS use when working with Angular Signals and HttpClient, toSignal, toObservable, or HTTP with signals."
metadata:
  version: 21.0.0
  generated_by: oguzhancart
  generated_at: 2026-02-19
---

# Angular Signals + HttpClient

**Version:** Angular 16+ (2025)
**Tags:** Signals, HTTP, toSignal, toObservable

**References:** [toSignal](https://angular.io/api/core/toSignal)

## Best Practices

- Use toSignal for HTTP

```ts
import { toSignal } from '@angular/core/rxjs-interop';

@Component({})
export class MyComponent {
  private http = inject(HttpClient);
  
  users = toSignal(this.http.get<User[]>('/api/users'), {
    initialValue: []
  });
}
```

- Use toObservable

```ts
import { toObservable, toSignal } from '@angular/core/rxjs-interop';

@Component({})
export class MyComponent {
  name = signal('John');
  name$ = toObservable(this.name);
}
```
