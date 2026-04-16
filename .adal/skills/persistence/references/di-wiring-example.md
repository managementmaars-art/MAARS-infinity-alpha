# DI Wiring Reference

When adding a new repository `FooRepo` backed by MongoDB collection `foo`, update these 4 files.
All other wiring (the `Symbols.Collections` mapping) is auto-generated — you don't touch it.

---

## 1. `src/enum/CollectionNameEnum.ts`

Add the new collection name. The value must match the real MongoDB collection name exactly.

```typescript
enum CollectionNameEnum {
    audit_log      = "audit_log",
    // ... existing entries ...
    foo            = "foo",          // ← add this
}
```

---

## 2. `src/db/ICollectionsDocument.ts`

Map the collection name string to its document type. This is what makes
`Symbols.Collections.foo` resolve to a typed `Collection<FooDocument>` throughout the codebase.

```typescript
import FooDocument from '../Documents/FooDocument.js';
// ... other imports ...

type ICollectionsDocument = Readonly<{
    audit_log: AuditLogDocument;
    // ... existing entries ...
    foo: FooDocument;               // ← add this
}>;
```

---

## 3. `src/di/Symbols.ts` — the `Repo` section

Add a symbol for the new repo. The string passed to `Symbol.for()` only needs to be unique
within the application — by convention it is the repo name.

```typescript
const Symbols = {
    // ...
    Repo: {
        // ... existing repos ...
        FooRepo: Symbol.for("FooRepo"),   // ← add this
    },
    // ...
};
```

> **Note:** You do **not** need to add to `Symbols.Collections`. The `convert()` helper at the
> top of the file auto-generates collection symbols from every key in `CollectionNameEnum`.

---

## 4. `src/di/container.ts`

Add the binding near the other repo registrations at the bottom of the file.

```typescript
// Repos — always inRequestScope
container.bind(Symbols.Repo.FooRepo).to(FooRepoImpl).inRequestScope(); // ← add this
```

Don't forget the import at the top:
```typescript
import FooRepoImpl from '~/repo/impl/FooRepoImpl.js';
```

### Scope guide

| Scope | Usage | Reason |
|---|---|---|
| `inSingletonScope` | `MongoClient`, typed `Collection<X>` instances | Created once, shared forever |
| `inRequestScope` | Repos, `IDatabaseContext` | One per HTTP request — ensures all repos in a request share the same session |
| `inTransientScope` | (Not commonly used here) | New instance on every injection |

`inRequestScope` is the correct scope for repos because it ensures all repos injected into the same HTTP request share the same `IDatabaseContext` instance, and therefore the same MongoDB `ClientSession`. This is what makes multi-repo use cases transactional — they all see and participate in the same transaction.

---

## Full example: adding `FooRepo`

Given a new entity `Foo` stored in collection `foo`:

### CollectionNameEnum.ts
```typescript
enum CollectionNameEnum {
    // ...existing...
    foo = "foo",
}
```

### ICollectionsDocument.ts
```typescript
import FooDocument from '../Documents/FooDocument.js';

type ICollectionsDocument = Readonly<{
    // ...existing...
    foo: FooDocument;
}>;
```

### Symbols.ts
```typescript
Repo: {
    // ...existing...
    FooRepo: Symbol.for("FooRepo"),
},
```

### container.ts
```typescript
import FooRepoImpl from '~/repo/impl/FooRepoImpl.js';

// (near the other repo bindings)
container.bind(Symbols.Repo.FooRepo).to(FooRepoImpl).inRequestScope();
```

After making these changes, run typecheck to verify everything is wired correctly.
