---
name: angular-viewchild
description: "ALWAYS use when working with Angular ViewChild, ContentChild, ViewChildren, or accessing DOM elements and child components in Angular."
metadata:
  version: 21.0.0
  generated_by: oguzhancart
  generated_at: 2026-02-19
---

# Angular ViewChild / ContentChild

**Version:** Angular 21 (2025)
**Tags:** ViewChild, ContentChild, DOM, Queries

**References:** [ViewChild API](https://angular.io/api/core/ViewChild) • [ContentChild API](https://angular.io/api/core/ContentChild)

## Best Practices

- Use ViewChild for element reference

```ts
import { ViewChild, ElementRef, AfterViewInit } from '@angular/core';

@Component({})
export class MyComponent implements AfterViewInit {
  @ViewChild('input') inputEl!: ElementRef<HTMLInputElement>;
  
  ngAfterViewInit() {
    this.inputEl.nativeElement.focus();
  }
}
```

- Use static option

```ts
// Static - available in ngOnInit
@ViewChild('static', { static: true }) staticEl!: ElementRef;

// Dynamic - available in ngAfterViewInit
@ViewChild('dynamic', { static: false }) dynamicEl!: ElementRef;
```

- Use ContentChild for projected content

```ts
import { ContentChild, TemplateRef } from '@angular/core';

@Component({
  selector: 'app-card',
  template: `
    <div class="card">
      <ng-content></ng-content>
    </div>
  `
})
export class CardComponent {
  @ContentChild(TemplateRef) headerTemplate!: TemplateRef<any>;
}
```

- Use ViewChildren for multiple elements

```ts
import { ViewChildren, QueryList } from '@angular/core';

@Component({})
export class ListComponent {
  @ViewChildren('item') items!: QueryList<ElementRef>;
  
  ngAfterViewInit() {
    this.items.forEach(item => console.log(item));
  }
}
```

- Use read option

```ts
@ViewChild('component', { read: ViewContainerRef }) container!: ViewContainerRef;

@ViewChild('template', { read: TemplateRef }) template!: TemplateRef<any>;
```

- Access component instance

```ts
@ViewChild(ChildComponent) child!: ChildComponent;

ngAfterViewInit() {
  this.child.doSomething();
}
```

- Use with signals

```ts
@ViewChild('el') el!: ElementRef<HTMLElement>;

ngAfterViewInit() {
  effect(() => {
    if (this.shouldFocus()) {
      this.el.nativeElement.focus();
    }
  });
}
```
