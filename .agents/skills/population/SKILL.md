---
name: population
description: >
  Add MongoDB population (eager-loading of related documents via aggregation $lookup pipelines)
  to an existing entity in a hexagonal architecture TypeScript project.
  Use this skill whenever the user says things like "populate Foo with its Bar",
  "add population support for FooEntity", "I need to eager-load related entities",
  "wire up the $lookup for Foo", "add the populate option to FooRepo",
  "create the shape and populator for Foo", "Foo needs to include its related Bar when fetched",
  or whenever someone needs to add optional relational data loading to an existing repository.
  Trigger even if the user just says "add population" without specifying the entity — ask them.
  Do NOT trigger for creating entities, DTOs, or base repositories from scratch (those are handled
  by entity and persistence skills).
---

# DAV Population Skill

Adds MongoDB population support — typed eager-loading of related documents via aggregation `$lookup` — to an existing entity. The entity, its DTO, document type, mapper, and repository are assumed to already exist. This skill only patches them where needed and writes the population infrastructure.

**Scope:** Shape type, QueryBuilder, Populator, plus targeted patches to entity, DTO, document, mapper, and repository interface/implementation.

**Does not:** create entities or repositories from scratch, write use cases, or manage DI container wiring.

---

## Phase 0 — Clarify Intent

If the user has not specified which entity to populate and/or which fields should be populated, use `AskUserQuestion` to ask:

1. Which entity needs population?
2. Which fields should be populatable, and for each:
   - What is the source collection/entity?
   - Is it a single value (1:1) or an array (1:many)?
   - Does the related entity itself have a populator already? (nested population)

Do not proceed until you have at least the entity name and one field to populate.

---

## Phase 1 — Discover the Project Structure

Before touching any file, orient yourself:

1. **Find the workspace lib prefix** — look at existing imports in `src/repo/` or `src/entity/`. It might be `@dav/lib`, `@myapp/lib`, `@workspace/lib`, etc. All examples below use `@workspace/lib` as placeholder.
2. **Find the collection enum** — typically `src/db/CollectionNameEnum.ts` or similar. You'll need the collection name constant for `$lookup`.
3. **Check for existing populators** — browse `src/repo/shape/`, `src/repo/populate/`, `src/repo/query/`. If any exist, read one to match the exact import style.
4. **Read the target entity** — `src/entity/FooEntity.ts`
5. **Read the target DTO** — `src/dto/IFoo.ts`
6. **Read the target document** — `src/db/Documents/FooDocument.ts`
7. **Read the target mapper** — `src/mapper/FooMapper.ts`
8. **Read the repository interface** — `src/repo/IFooRepo.ts`
9. **Read the repository implementation** — `src/repo/impl/FooRepoImpl.ts`

If `src/repo/shape/` or `src/repo/populate/` directories do not yet exist, create them.

---

## Phase 2 — Patch Satellite Files

Patch each file only where something is actually missing. Do not rewrite files wholesale.

### 2a. Entity

For each populated field `bar` on entity `Foo`:

- **Props type** must include an optional field for the populated value:
  - 1:1 → `bar: Bar | null` (initialized to `null` in `create()`)
  - 1:many via foreign key on Bar → `bars: Bar[]` (initialized to `[]` in `create()`)
- **`create()` static method** — if the populated field has a meaningful default, accept it as an optional param. Typically `bar` is not passed to `create()` (it starts null/empty and is filled by the mapper after aggregation).
- **`toDTO()`** — if the DTO has an optional `bar?` field, map it: `bar: this.props.bar?.toDTO() ?? null`.
- **Getter** — add `get bar(): Bar | null` (or `Bar[]`) if missing.
- **No `populateBar()` mutation method needed** — the mapper sets the field directly after aggregation.

### 2b. DTO

For each populated field `bar` on `IFoo`:

- Add `bar?: IBar | null` (optional — it may or may not be present depending on query).
- For 1:many: `bars?: IBar[]`.
- If the DTO lives inside a namespace, add the field to the correct variant.
- If a separate `index.ts` re-exports the DTO, no change needed there unless you added a new sub-type.

### 2c. Document

For each populated field `bar` on `FooDocument`:

- Add `bar?: BarDocument | null` (always optional — absent on raw stored documents, present only after `$lookup`).
- For 1:many: `bars?: BarDocument[]`.
- The FK reference field (`bar_id: ObjectId | null`) should already be present; do not add a second FK.

### 2d. Mapper

For each populated field `bar`, update `FooMapper.from()`:

```typescript
// After building the base entity:
if (doc.bar) {
    entity.props.bar = BarMapper.from(doc.bar);
}
// or for arrays:
if (doc.bars) {
    entity.props.bars = doc.bars.map(BarMapper.from);
}
```

The `to()` direction (entity → document) should **not** include populated fields — they are loaded, not saved, through this path.

---

## Phase 3 — Write Population Core Files

Read the reference files before writing:
- `references/shape-example.ts` — Shape types (leaf vs nested)
- `references/query-builder-example.ts` — QueryBuilder with `populateWith()`
- `references/populator-example.ts` — flat Populator (no nesting)
- `references/populator-nested-example.ts` — nested Populator delegating to sub-populator

### 3a. Shape — `src/repo/shape/FooShape.ts`

```typescript
// Leaf fields use `true`; fields whose related entity is also populatable use that entity's Shape type.
import type { BarShape } from './BarShape.js'; // only if Bar also has a populator

export type FooShape = {
    bar: true;           // 1:1, leaf — Bar has no further population
    items: true;         // 1:many, leaf
    baz: BazShape;       // 1:1, nested — Baz itself has populatable fields
};
```

### 3b. QueryBuilder — `src/repo/query/FooQueryBuilder.ts`

```typescript
import { normalizePopulate, type Populate } from '@workspace/lib';
import FooDocument from '~/db/Documents/FooDocument.js';
import FooPopulator from '../populate/FooPopulator.js';
import type { FooShape } from '../shape/FooShape.js';
import QueryBuilder from './QueryBuilder.js';

export default class FooQueryBuilder extends QueryBuilder<FooDocument> {
    populateWith(fields: Populate<FooShape> = {}): this {
        const normalized = normalizePopulate(fields, FooPopulator.SHAPE);
        const pipeline = FooPopulator.buildPipeline(normalized);
        this.push_populate_pipeline(pipeline);
        return this;
    }
}
```

### 3c. Populator — `src/repo/populate/FooPopulator.ts`

For each field:
- **1:1 relationship** (Bar lives in its own collection, Foo stores `bar_id`): use `lookup` + `unwind`.
- **1:many relationship** (Bar stores `foo_id` as FK, or Foo stores an array of IDs): use `lookup` only, no `unwind`.
- **Nested population** (Bar itself has a populator): pass a sub-pipeline to the `lookup`. See `references/populator-nested-example.ts`.

```typescript
import { BasePopulator, type NormalizedPopulate } from '@workspace/lib';
import CollectionNameEnum from '~/db/CollectionNameEnum.js';
import type TCollectionName from '~/db/TCollectionName.js';
import type { FooShape } from '../shape/FooShape.js';

export default class FooPopulator extends BasePopulator<FooShape, TCollectionName> {
    static readonly SHAPE: FooShape = {
        bar: true,
        items: true,
    };

    private bar(): void {
        if (!this.markPopulated('bar')) return;
        this.addStages(
            this.lookup({
                from: CollectionNameEnum.bar,   // collection name constant
                localField: 'bar_id',           // FK on Foo document
                foreignField: '_id',
                as: 'bar',
            }),
            this.unwind('bar'),                 // 1:1 — flatten array to single object
        );
    }

    private items(): void {
        if (!this.markPopulated('items')) return;
        this.addStages(
            this.lookup({
                from: CollectionNameEnum.item,
                localField: '_id',              // Foo's own _id
                foreignField: 'foo_id',         // FK on Item documents
                as: 'items',
            }),
            // No unwind — keeps the array
        );
    }

    populate(spec: NormalizedPopulate<FooShape>): this {
        if (spec.bar) this.bar();
        if (spec.items) this.items();
        return this;
    }

    static buildPipeline(spec: NormalizedPopulate<FooShape>): import('mongodb').Document[] {
        return new FooPopulator().populate(spec).build();
    }
}
```

---

## Phase 4 — Patch the Repository

### 4a. Repository Interface — `src/repo/IFooRepo.ts`

Add the `Options` namespace with a `populate` field, and add `options?` param to every query method (save/saveMany/delete do not need it):

```typescript
import type { Populate } from '@workspace/lib';
import type { FooShape } from './shape/FooShape.js';

interface IFooRepo {
    search(query: IFooRepo.Search, options?: IFooRepo.Options): Promise<Foo[]>;
    get(id: ObjectId, options?: IFooRepo.Options): Promise<Maybe<Foo>>;
    findByIds(ids: ObjectId[], options?: IFooRepo.Options): Promise<Foo[]>;
    // ... other query methods
    save(entity: Foo): Promise<void>;
}

namespace IFooRepo {
    export type Options = {
        populate?: Populate<FooShape>;
    };
}

export default IFooRepo;
```

### 4b. Repository Implementation — `src/repo/impl/FooRepoImpl.ts`

Switch each query method to use `FooQueryBuilder` with `.populateWith(options?.populate)`:

```typescript
async get(id: ObjectId, options?: IFooRepo.Options): Promise<Maybe<Foo>> {
    const pipeline = new FooQueryBuilder()
        .match({ _id: id } as Filter<FooDocument>)
        .populateWith(options?.populate)
        .limit(1)
        .build();

    const results = await this.coll.aggregate<FooDocument>(
        pipeline, { session: this.db.session }
    ).toArray();

    if (results.length === 0) return Maybe.none();
    return Maybe.maybe(FooMapper.from(results[0]!));
}
```

Methods that already use `aggregate()` just need `.populateWith(options?.populate)` inserted into the builder chain. Methods that use `findOne()` or `find()` should be converted to `aggregate()` with the QueryBuilder.

---

## Special Cases

### Polymorphic entity (discriminated union)
If `Foo` has a `type` discriminator and different variants have different populatable fields:
- The Shape can include all fields across variants: `{ fontFile: true; rasterFile: true; vectorFile: true; }`.
- In the populator, each private method populates only the relevant field — because `$lookup` on a non-existent FK just returns an empty array, which is then dropped by `unwind` or ignored.
- Alternatively, if the variant shapes are completely disjoint, create separate Shape types with a union.

### Nested population (the related entity also has a populator)
When `Bar` itself has a `BarPopulator`, you can pass a sub-pipeline into the `$lookup`:
```typescript
private bar(nestedSpec: NormalizedPopulate<BarShape>): void {
    if (!this.markPopulated('bar')) return;
    const nestedPipeline = BarPopulator.buildPipeline(nestedSpec);
    this.addStages(
        this.lookup({
            from: CollectionNameEnum.bar,
            localField: 'bar_id',
            foreignField: '_id',
            as: 'bar',
            pipeline: nestedPipeline,    // <-- sub-population
        }),
        this.unwind('bar'),
    );
}
```
The Shape field must then be typed as `BarShape` (not `true`), and the `populate()` method receives `spec.bar` as a `NormalizedPopulate<BarShape>`.

### `$lookup` with `$in` (Foo stores an array of IDs)
When `Foo.bar_ids` is an array of ObjectIds pointing to Bar documents:
```typescript
this.lookup({
    from: CollectionNameEnum.bar,
    localField: 'bar_ids',   // array field on Foo
    foreignField: '_id',
    as: 'bars',
})
// No unwind — result is an array matching the IDs
```

### Optional relationship (FK can be null)
For `bar_id: ObjectId | null`, the `$lookup` returns an empty array when FK is null. Use:
```typescript
this.addStages(
    this.lookup({ from: CollectionNameEnum.bar, localField: 'bar_id', foreignField: '_id', as: 'bar' }),
    this.unwind('bar', { preserveNullAndEmptyArrays: true }),
);
```
Then in the mapper: `entity.props.bar = doc.bar ? BarMapper.from(doc.bar) : null`.

---

## Phase 5 — Typecheck

Run the typecheck command for the core package then fix any errors before considering the task done.

---

## Reference Files

- `references/shape-example.ts` — Shape type examples with comments
- `references/query-builder-example.ts` — Full QueryBuilder
- `references/populator-example.ts` — Flat populator (leaf fields only)
- `references/populator-nested-example.ts` — Populator with nested sub-population
