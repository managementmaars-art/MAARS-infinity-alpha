---
name: angular-signals-forms
description: "ALWAYS use when working with Angular Signal Forms, reactive forms with signals, FormControl with signals, or new forms API in Angular."
metadata:
  version: 21.0.0
  generated_by: oguzhancart
  generated_at: 2026-02-19
---

# Angular Signal Forms

**Version:** Angular 19+ (2025)
**Tags:** Signal Forms, Reactive Forms, Signals

**References:** [Signal Forms](https://angular.dev/guide/forms/signal-forms)

## Best Practices

- Use signal-based FormControl

```ts
import { signal } from '@angular/forms';

@Component({})
export class MyComponent {
  name = signal('');
  
  updateName(value: string) {
    this.name.set(value);
  }
}
```

- Use withValidators

```ts
email = signal('', {
  validators: [Validators.required, Validators.email]
});
```

- Use withAsyncValidators

```ts
username = signal('', {
  asyncValidators: [uniqueUsernameValidator]
});
```
