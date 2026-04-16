---
name: entity
description: Create or modify domain entities in the core package of this monorepo. Use this skill whenever the user asks to add a new entity, update an existing entity, add properties or methods to an entity, or work on the entity/dto layer in the core package. Trigger when the user says things like "create a Foo entity", "add a field to Bar", "I need a new domain object", or "add entity X to core". Also trigger for DTO creation or modification.
---

# DAV Entity Skill

This skill helps you create or modify domain entities following the hexagonal architecture conventions of this project. **Scope: entity class + DTO interface only** — persistence (repository, mapper, MongoDB document) is a separate concern handled elsewhere.

## Before You Write Anything

Read the existing codebase before generating code:
1. Locate the entity directory (typically `packages/core/src/entity/`) and read a similar existing entity as a reference
2. Locate the DTO directory (typically `packages/core/src/dto/`) and read a similar DTO
3. Check for a `CLAUDE.md` inside the entity directory — it may have project-specific conventions

**If the project is new or the entity/dto directories are empty**, use the reference files in this skill's `references/` directory as your canonical examples instead:
- `references/entity-example.ts` — fully annotated entity covering every pattern
- `references/dto-example.ts` — fully annotated DTO covering every pattern
- `references/entity-union.ts` — entity union pattern: abstract base + multiple concrete subtypes discriminated by a `type` literal
- `references/dto-union.ts` — DTO union pattern: base interface + concrete sub-interfaces each carrying a `type` literal discriminant

These reference files cover all the patterns described below. Read them before generating code on a fresh project — they contain inline comments explaining the *why* behind each convention.

---

## File Structure

For a **new entity** you'll create two files:
- `src/dto/IEntityName.ts` — the public data contract (DTO interface)
- `src/entity/EntityName.ts` — the domain entity class

Then export both from their respective index files.

For **modifying an existing entity**, read the files first, then apply changes consistently across both.

---

## DTO Interface

The DTO is the public serialization contract. It has no methods — pure native data types.

```typescript
// src/dto/IEntityName.ts
export default interface IEntityName {
    _id: string;            // always string (serialized from ObjectId or UUID)
    name: string;
    description: string;
    slug?: string;
    deleted_at: string | null;  // DateTime serialized as ISO string
    // foreign keys end with _id: string
    parent_id: string | null;
}
```

**Rules:**
- All properties `snake_case`
- Primary key: `_id: string`
- Foreign keys: `parent_id`, `elemento_id`, etc.
- `DateTime` → `string` (ISO); nullable → `string | null`
- No methods, no business logic
- Only native types (string, number, boolean, arrays, nested DTOs) — no domain types or value objects here (use their DTO representation instead if needed)
- 1 entity = 1 DTO interface;

---

## Entity Class

```typescript
// src/entity/EntityName.ts
import { Entity, IEntity } from "@dav/lib";
import { DateTime } from "luxon";
import { ObjectId } from "mongodb";  // or UUID — check what the project uses
import { Result, Maybe } from "@dav/lib/monad";
import IEntityName from "~/dto/IEntityName.js";

type EntityNameProps = {
    name: string;
    description: string;
    deleted_at: DateTime<true> | null;
    // Use domain types, not primitives for complex concepts
    // e.g. email: EmailAddress  (not string)
};

export default class EntityName extends Entity<EntityNameProps, ObjectId> implements IEntity<ObjectId> {
    constructor(props: EntityNameProps, id?: ObjectId) {
        super(props, new ObjectId(id));  // always wrap in ID constructor
    }

    // Getters — one per prop, no setters unless business-justified
    get name(): string { return this.props.name; }
    get description(): string { return this.props.description; }

    // Business methods — describe intent, not data access
    // Return Result<T, Error> for fallible operations
    // Return void for infallible mutations
    someOperation(input: string): Result<void, Error> {
        if (!input) return Result.err(new Error("Invalid input"));
        this.props.name = input;
        return Result.ok(undefined);
    }

    toDTO(): IEntityName {
        return {
            _id: this._id.toHexString(),      // ObjectId → string
            // _id: this._id.toString(),       // UUID → string
            name: this.props.name,
            description: this.props.description,
            deleted_at: this.deleted_at?.toISO() ?? null,
            // nested entity: this.props.nested?.toDTO() ?? null
            // array: this.props.items.map(i => i.toDTO())
        };
    }

    static create(props: {
        name?: string;
        description?: string;
        deleted_at?: DateTime<true> | null;
        // all props optional — use ?? to apply defaults
    }, id?: ObjectId) {
        return new EntityName({
            name: props.name ?? "",
            description: props.description ?? "",
            deleted_at: props.deleted_at ?? null,
        }, id);
    }
}
```

**Key rules:**
- Constructor: `super(props, new ObjectId(id))` — wraps id even if already the right type
- **Never instantiate directly from outside** — always go through `static create()`
- The majority of `create()` props are optional with `??` defaults, required fields are the ones strictly necessary (usually dictated by business rules, not technical ones)
- Getters for everything; only add setters when the operation has business meaning
- `deleted_at` pattern: `DateTime<true> | null` for soft deletes

### Inheritance

When extending a base entity class:
```typescript
type EntityNameProps = BaseProps & { extraField: string; };

class EntityName extends BaseClass<EntityNameProps, ObjectId> {
    override toDTO(): IEntityName {
        return { ...super.toDTO(), extraField: this.props.extraField };
    }
}
```

For the **union + abstract base** pattern (multiple concrete subtypes distinguished by a `type` literal), read `references/entity-union.ts` (entities) and `references/dto-union.ts` (DTOs). Both files use matching type names and discriminants so you can see the entity↔DTO correspondence directly.

---

## Audit trail pattern

For entities that track who changed what:
```typescript
// In props:
created_at: DateTime;
updated_at: DateTime;
updated_by: Operator | null;  // import the Operator entity

// In business methods that mutate state:
this.props.updated_at = DateTime.now();
this.props.updated_by = operator;
```

## Value objects

Prefer value objects for complex domain concepts rather than raw primitives. Check the project's `src/value_object/` directory for what's available before defaulting to `string`. Common ones:
- Email → `EmailAddress`
- Password → `Password`
- If the concept doesn't have an existing value object, use a plain type for now and note that it could become one.

---

## Exports

Add to `src/entity/index.ts`:
```typescript
export { default as EntityName } from "./EntityName.js";
```

Add to `src/dto/index.ts`:
```typescript
export type { default as IEntityName } from "./IEntityName.js";
```

---

## Checklist — New Entity

- [ ] Read a comparable existing entity first
- [ ] DTO created in `src/dto/IEntityName.ts` with `_id: string`
- [ ] Entity class in `src/entity/EntityName.ts` with `create()` factory
- [ ] All props have getters; `create()` has optional props with `??` defaults
- [ ] `toDTO()` maps every DTO field; ID converted to string
- [ ] Both exported from their index files
- [ ] Run typecheck

## Checklist — Modifying Existing Entity

- [ ] Read the entity file and DTO file first
- [ ] New prop added to `EntityNameProps` type
- [ ] Getter added
- [ ] `create()` updated with optional prop + default
- [ ] `toDTO()` updated to include new field
- [ ] DTO interface updated
- [ ] Run typecheck
