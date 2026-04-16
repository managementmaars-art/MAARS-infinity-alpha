---
name: persistence
description: >
  Implement the MongoDB persistence layer for a hexagonal architecture TypeScript project.
  Use this skill whenever the user needs to create or modify a repository interface,
  repository implementation, MongoDB document type, or entity mapper.
  Trigger when the user says things like "create a repo for Foo", "add a mapper for Bar",
  "I need to persist Baz to MongoDB", "add the persistence layer for X",
  "write the document type for Foo", "create repository and mapper", "wire up Foo to the database",
  or whenever a domain entity exists and the storage layer is missing or incomplete.
  Also trigger when the user modifies an entity and says the persistence files need to stay in sync,
  or when they reference repo/mapper/document files by name.
---

# DAV Persistence Skill

Helps you build the persistence layer — document type, repository interface, implementation, and mapper — for a hexagonal architecture TypeScript/MongoDB project following the ports-and-adapters pattern.

**Scope:** document type, repository interface, repository implementation, mapper.
Population (the system for eager-loading related entities via aggregation pipelines) is a separate concern with its own skill — this skill only declares the hook for it where needed, without implementing the internal machinery.

**Assumes** the entity class and DTO interface already exist and are correct. Read them before writing any persistence code.

---

## Before You Write Anything

1. **Read the entity and DTO** — identify which fields need type conversion (DateTime → Date, string id → ObjectId, value objects → their serialized form) vs. scalars that pass through unchanged.
2. **Scan an existing repo in the project** — browse `src/repo/`, `src/repo/impl/`, `src/mapper/`, `src/db/Documents/`. Match the existing code style: import order, mapper shape, whether they use `Foo.create()` or `new Foo()` in mappers.
3. **Find the workspace prefix** — check existing imports for the shared library (e.g., `@dav/lib`, `@myapp/lib`). Examples below use `@workspace/lib` as a placeholder.
4. **If the project has few existing repo examples**, read the reference files — they are fully annotated and workspace-agnostic:
   - `references/simple-repo-example.ts` — no population, uses `.find()`/`.findOne()` directly
   - `references/aggregate-repo-example.ts` — optional population, aggregation pipeline, streaming, bulk save
   - `references/di-wiring-example.md` — the exact 4 files to update for DI registration

---

## What Gets Created

For a new entity `Foo` stored in collection `foo`:

| File | Location |
|---|---|
| Document type | `src/db/Documents/FooDocument.ts` |
| Repository interface | `src/repo/IFooRepo.ts` |
| Repository implementation | `src/repo/impl/FooRepoImpl.ts` |
| Mapper | `src/mapper/FooMapper.ts` |

Plus **4 existing files** to update for DI registration (see [DI Wiring](#di-wiring)).

---

## Document Type

The document type is the MongoDB-level view of the entity. It's a pure TypeScript type alias — not a class, not a schema.

```typescript
// src/db/Documents/FooDocument.ts
import { ObjectId } from "mongodb";
import IFoo from "~/dto/IFoo.js";
import BarDocument from "./BarDocument.js";

type FooDocument = Overwrite<IFoo, {
    _id: ObjectId;              // DTO has string → document has ObjectId
    deleted_at: Date | null;    // DTO has string|null → document has JS Date|null
    owner_id: ObjectId | null;  // FK: DTO string → document ObjectId
    bar?: BarDocument | null;   // optional — only present after aggregation $lookup
    items?: ItemDocument[];     // optional array — only after aggregation
}>;

export default FooDocument;
```

**Rules:**
- Start from `Overwrite<IDTO, {...}>` and override only what differs from the DTO.
- If some DTO fields are computed (never stored in MongoDB), wrap with `Omit<IFoo, "computed_field">` before overriding: `Overwrite<Omit<IFoo, "labels">, {...}>`.
- `_id` is always `ObjectId`.
- `DateTime` in entity/DTO becomes `Date` in document; FK fields (`*_id`) become `ObjectId`.
- Populated sub-documents are always **optional** (`?`) — they're absent on raw stored documents, present only when an aggregation pipeline joined them.
- Polymorphic collections use discriminated unions: `type XDocument = ADocument | BDocument`.

---

## Repository Interface

```typescript
// src/repo/IFooRepo.ts
import { Maybe } from "@workspace/lib/monad";
import { ObjectId } from "mongodb";
import Foo from "~/entity/Foo.js";

// Export the search query type alongside the interface
export type SearchFoo = {
    name?: string;
    include_deleted?: boolean;
};

interface IFooRepo {
    search(query: SearchFoo): Promise<Foo[]>;   // empty array when nothing matches
    get(id: ObjectId): Promise<Maybe<Foo>>;     // Maybe.none() when not found
    save(entity: Foo): Promise<void>;
}

export default IFooRepo;
```

**Return type guide:**
| Scenario | Return type |
|---|---|
| Nullable single result | `Promise<Maybe<T>>` |
| Multiple results | `Promise<T[]>` — never Maybe; empty array is fine |
| Write | `Promise<void>` |
| Count | `Promise<number>` |
| Large result set | `Readable` (stream) |

**When population is needed** — declare an `options` parameter and a namespace with an `Options` type. The population skill handles everything else; the interface just exposes the hook:

```typescript
interface IFooRepo {
    search(query: SearchFoo, options?: IFooRepo.Options): Promise<Foo[]>;
    get(id: ObjectId, options?: IFooRepo.Options): Promise<Maybe<Foo>>;
    save(entity: Foo): Promise<void>;
}

namespace IFooRepo {
    export type Options = {
        populate?: Populate<FooShape>; // Populate + FooShape come from the population system
    };
}
```

---

## Repository Implementation

```typescript
// src/repo/impl/FooRepoImpl.ts
import { Maybe } from "@workspace/lib/monad";
import { inject, injectable } from "inversify";
import { Collection, Filter, ObjectId } from "mongodb";
import type IDatabaseContext from "~/db/Context/IDatabaseContext.js";
import FooDocument from "~/db/Documents/FooDocument.js";
import Symbols from "~/di/Symbols.js";
import Foo from "~/entity/Foo.js";
import FooMapper from "~/mapper/FooMapper.js";
import IFooRepo, { SearchFoo } from "../IFooRepo.js";

@injectable()
export default class FooRepoImpl implements IFooRepo {
    constructor(
        @inject(Symbols.Collections.foo) private readonly coll: Collection<FooDocument>,
        @inject(Symbols.DatabaseContext) private readonly db: IDatabaseContext,
    ) {}

    async search(query: SearchFoo): Promise<Foo[]> {
        const filter: Filter<FooDocument> = {};
        if (query.name) filter.name = new RegExp(`^${query.name}`, "i");
        if (!query.include_deleted) filter.deleted_at = null;

        const docs = await this.coll
            .find(filter, { session: this.db.session }) // session is required — wires into transactions
            .sort({ name: 1 })
            .toArray();
        return docs.map(FooMapper.from);
    }

    async get(id: ObjectId): Promise<Maybe<Foo>> {
        const doc = await this.coll.findOne({ _id: id }, { session: this.db.session });
        return Maybe.maybe(doc).map(FooMapper.from);
    }

    async save(entity: Foo): Promise<void> {
        const raw = FooMapper.to(entity);
        await this.coll.updateOne(
            { _id: raw._id },
            { $set: raw },
            { upsert: true, session: this.db.session },
        );
    }
}
```

**The session rule** — every MongoDB driver call must include `{ session: this.db.session }`. Without it, the call silently runs outside any active transaction. `IDatabaseContext` exposes `session` as `undefined` when there's no transaction; the MongoDB driver ignores `undefined` gracefully, so it's always safe to pass.

**Simple vs. aggregate reads:**
- Use `.find()`/`.findOne()` for straightforward queries with no population.
- When the repo supports population, use an aggregation pipeline built via `XQueryBuilder`. The query builder is part of the population system — see `references/aggregate-repo-example.ts` for the pattern.

---

## Mapper

The mapper is a plain object (not a class) that transforms between entity and document.

```typescript
// src/mapper/FooMapper.ts
import { IEntityMapper } from "@workspace/lib";
import { DateTime } from "luxon";
import FooDocument from "~/db/Documents/FooDocument.js";
import Foo from "~/entity/Foo.js";

const FooMapper: IEntityMapper<Foo, FooDocument> = {
    /**
     * from: document → entity (read path)
     * Convert MongoDB types to domain types. Patch in populated sub-documents after construction.
     */
    from: (doc: FooDocument): Foo => {
        const entity = new Foo({
            name: doc.name,
            owner_id: doc.owner_id,
            deleted_at: doc.deleted_at
                ? DateTime.fromJSDate(doc.deleted_at) as DateTime<true>
                : null,
            bar: null,   // default; overwritten below if the pipeline populated it
        }, doc._id);

        if (doc.bar) entity.props.bar = BarMapper.from(doc.bar);
        if (doc.items) entity.props.items = doc.items.map(ItemMapper.from);

        return entity;
    },

    /**
     * to: entity → document (write path)
     * Only include fields the collection actually stores. Populated join results are never written back.
     */
    to: (domain: Foo): FooDocument => ({
        _id: domain._id,
        name: domain.props.name,
        owner_id: domain.props.owner_id,
        deleted_at: domain.deleted_at?.toJSDate() ?? null,
    }),
};

export default FooMapper;
```

**`from` vs. `to` asymmetry** — `from` is read-time and may encounter in-place populated sub-documents from an aggregation; construct the entity, then patch them in. `to` is write-time; serialize only own stored scalar fields and FK ObjectIds — never populated relations.

**`new Foo()` vs. `Foo.create()`** — in mappers, the direct constructor is appropriate because you have complete, already-validated stored state and don't need `create()`'s defaults. Use `Foo.create()` in use cases where you're working with partial user input.

**Two mapper styles in the wild** — some projects use `namespace FooMapper { export function from(...) }`. Match what already exists in the project.

---

## DI Wiring

Touch these 4 files when adding a new collection. See `references/di-wiring-example.md` for exact code snippets.

1. `src/enum/CollectionNameEnum.ts` — add `foo = "foo"`
2. `src/db/ICollectionsDocument.ts` — add `foo: FooDocument`
3. `src/di/Symbols.ts` — add `FooRepo: Symbol.for("FooRepo")` in the `Repo` section
4. `src/di/container.ts` — add `container.bind(Symbols.Repo.FooRepo).to(FooRepoImpl).inRequestScope()`

`Symbols.Collections` is auto-generated from `CollectionNameEnum` — you do **not** need to touch it manually.

---

## Special Cases

### Soft-delete

Entity has `deleted_at: DateTime<true> | null`. Records stay in the collection; filtered omitting deleted by default.

```typescript
// In save():
if (entity.isDeleted()) {
    await this.coll.updateOne(
        { _id: raw._id },
        { $set: { deleted_at: entity.deleted_at!.toJSDate() } },
        { session: this.db.session },
    );
} else {
    await this.coll.updateOne({ _id: raw._id }, { $set: raw }, { upsert: true, session: this.db.session });
}

// In search() filter:
if (!query.include_deleted) filter.deleted_at = null;
```

### Hard-delete

```typescript
if (entity.isDeleted()) {
    await this.coll.deleteOne({ _id: raw._id }, { session: this.db.session });
} else {
    await this.coll.updateOne({ _id: raw._id }, { $set: raw }, { upsert: true, session: this.db.session });
}
```

### Bulk save via `saveMany`

```typescript
import prepareBulkOps from "~/db/prepareBulkOps.js";

async saveMany(entities: Foo[]): Promise<void> {
    const ops = prepareBulkOps(entities, FooMapper);
    if (!ops.length) return;
    await this.coll.bulkWrite(ops, { session: this.db.session });
}
```

### Saving child entities from a parent repo

When a parent's `save()` must also persist child entities in their own collection:

```typescript
constructor(
    @inject(Symbols.Collections.foo) private readonly coll: Collection<FooDocument>,
    @inject(Symbols.Repo.BarRepo) private readonly barRepo: IBarRepo,  // inject child repo
    @inject(Symbols.DatabaseContext) private readonly db: IDatabaseContext,
) {}

async save(entity: Foo): Promise<void> {
    const raw = FooMapper.to(entity);
    await this.coll.updateOne({ _id: raw._id }, { $set: raw }, { upsert: true, session: this.db.session });
    await this.barRepo.saveMany(entity.bars); // delegate to child repo — same transaction session
}
```

### Polymorphic collections

When one MongoDB collection stores multiple entity variants:

```typescript
// Document: discriminated union
type FooDocument = FooADocument | FooBDocument; // each has `type: "A" | "B"` discriminator

// Mapper: dispatch on doc.type
from: (doc: FooDocument): Foo => {
    if (doc.type === "A") return FooAMapper.from(doc as FooADocument);
    if (doc.type === "B") return FooBMapper.from(doc as FooBDocument);
    throw new Error(`Unknown Foo type: ${(doc as any).type}`);
}
```

### Streaming large result sets

Use a `Readable` with cursor iteration rather than `.toArray()` to avoid loading the full collection into memory. See `references/aggregate-repo-example.ts` for the complete streaming implementation pattern.

---

## Checklist — New Repository

- [ ] Read the entity + DTO before writing anything
- [ ] `FooDocument.ts` created with `Overwrite<IFoo, {_id: ObjectId; ...}>`
- [ ] `IFooRepo.ts` created with interface + exported search type
- [ ] `FooRepoImpl.ts` created — `@injectable()`, every call passes `{ session: this.db.session }`
- [ ] `FooMapper.ts` created — `from()` handles optional populated fields; `to()` only own stored scalars
- [ ] `CollectionNameEnum` updated
- [ ] `ICollectionsDocument` updated
- [ ] `Symbols.Repo.FooRepo` added
- [ ] `container.bind(...).inRequestScope()` added
- [ ] run typecheck

## Checklist — Modifying Existing

- [ ] Read all four files before changing anything
- [ ] New field → update `FooDocument` + `FooMapper.from()` + `FooMapper.to()` + interface if the signature changes
- [ ] run typecheck
