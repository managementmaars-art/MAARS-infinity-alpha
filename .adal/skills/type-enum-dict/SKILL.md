---
name: type-enum-dict
description: |
  Create, update, or maintain TypeScript type unions, template literal types, runtime enums, and dict mappings in a monorepo core package. Use this skill whenever the user needs to express a finite set of string values (states, phases, categories, MIME types, formatted strings) or needs the runtime enum version, human-readable labels, or value-mapping dicts for those types. Trigger on: "add a type for X", "create an enum for Y", "add a dict/description for Z", "add a state/phase type", "I need a list of X values at runtime", "map X to labels", "add a template literal type", or when creating/editing an entity that needs a constrained string field.
---

# Type / Enum / Dict Skill

This skill covers three tightly-related artifacts created together whenever a domain concept needs a constrained string type at compile time and/or at runtime.

## The three artifacts

### Type (`src/type/T{Name}.ts`)
Pure TypeScript — no runtime value. Three variants:

**String union** — for finite known values:
```ts
type TPublishState = "draft" | "published";
export default TPublishState;
```

**Template literal** — for structured string shapes validated statically by the type system:
```ts
type TSimpleDate = `${number}-${number}-${number}`;
export default TSimpleDate;
```

**Namespace-augmented** — when sub-groups of the union are useful independently:
```ts
type TContentType =
  | TContentType.Raster
  | TContentType.Vector;

namespace TContentType {
  export type Raster = "image/png" | "image/jpeg";
  export type Vector = "image/svg+xml";
}
export default TContentType;
```

> Template literal types generally don't need an Enum or Desc — there are no finite members to enumerate.

---

### Enum (`src/enum/{Name}Enum.ts`)
Runtime identity record: every key equals its value. Relies on the global utility type `Enum<T> = { [K in T]: K }` (no import needed — it's a global declaration).

```ts
import TPublishState from "../type/TPublishState.js";

const PublishStateEnum: Enum<TPublishState> = {
  draft: "draft",
  published: "published",
};
export default PublishStateEnum;
```

Use `Object.values(SomeEnum)` to get an array of all members at runtime.

The type source can also come from a DTO interface member instead of a dedicated type file:
```ts
import IMyDto from "../dto/IMyDto.js";
const MyRoleEnum: Enum<IMyDto.Role> = { admin: "admin", viewer: "viewer" };
```

---

### Dict (`src/dict/{Name}Desc.ts`)
Maps every union member to a string. Relies on the global utility type `Desc<T> = { [K in T]: string }`. Prefer using the enum constants as computed keys — this avoids magic strings and ensures the dict stays in sync with the enum.

**Label dict** — human-readable display values:
```ts
import TPublishState from "../type/TPublishState.js";
import PublishStateEnum from "../enum/PublishStateEnum.js";

const PublishStateDesc: Desc<TPublishState> = {
  [PublishStateEnum.draft]: "Draft",
  [PublishStateEnum.published]: "Published",
};
export default PublishStateDesc;
```

**Value-mapping dict** — when the mapped value is not a label (e.g. file extension, icon name, color):
```ts
// Name the file to signal the mapping direction: {Target}From{Source}.ts
const ExtensionFromContentType: Desc<TContentType> = {
  "image/png": "png",
  "image/svg+xml": "svg",
};
export default ExtensionFromContentType;
```

---

## File naming conventions

| Artifact | File | Export name |
|----------|------|-------------|
| Type | `src/type/T{Name}.ts` | `TName` (default) |
| Enum | `src/enum/{Name}Enum.ts` | `{Name}Enum` (default) |
| Label dict | `src/dict/{Name}Desc.ts` | `{Name}Desc` (default) |
| Value-mapping dict | `src/dict/{Target}From{Source}.ts` | descriptive (default) |

---

## Barrel exports

Always update the barrel index after creating a file.

`src/type/index.ts` — type-only re-exports:
```ts
export type { default as TPublishState } from "./TPublishState.js";
```

`src/enum/index.ts` and `src/dict/index.ts` — value re-exports:
```ts
export { default as PublishStateEnum } from "./PublishStateEnum.js";
export { default as PublishStateDesc } from "./PublishStateDesc.js";
```

---

## Path aliases

Use the package's configured path alias for cross-directory imports (e.g. `~/type/...`, `~/enum/...`). Check `tsconfig.json` for the alias prefix — don't hardcode deep relative paths.

---

## Decision guide

| Situation | What to create |
|-----------|----------------|
| Finite string values (states, phases, categories) | Type + Enum + Desc |
| Structured string shape (date, time, code pattern) | Type only |
| Values with logical sub-groups (e.g. MIME types by category) | Type with namespace sub-types |
| Need to map each member to a non-label value | Additional value-mapping dict |
| Type already exists on a DTO interface | Enum only (skip type file) |

---

## Workflow

1. Identify the concept and its values (or pattern for template literals).
2. Create the type file.
3. Create the enum file (skip for template literals).
4. Create the dict file(s) — clarify with the user what label or mapping is needed if not obvious from context.
5. Add all new files to their respective `index.ts` barrel.
6. Run `typecheck` to verify — the `Enum<T>` and `Desc<T>` constraints will catch any missing or extra members at compile time.
