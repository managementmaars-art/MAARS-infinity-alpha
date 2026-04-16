/**
 * Shape type examples for the population skill.
 *
 * A Shape is a pure TypeScript type that declares which fields of an entity
 * can be populated (eager-loaded via MongoDB $lookup). The repository exposes
 * a `Populate<FooShape>` option that callers use to request specific fields.
 *
 * WORKSPACE NOTE: Replace `@workspace/lib` with the actual lib package name
 * in your project (e.g. `@dav/lib`, `@myapp/lib`).
 */

// ---------------------------------------------------------------------------
// 1. Leaf Shape — every field is `true` (no further nesting)
// ---------------------------------------------------------------------------

/**
 * FooShape: Foo can eager-load two related entities.
 * - `category` is a single related document (1:1 via category_id FK)
 * - `tags` is an array of related documents (1:many via tag.foo_id FK)
 *
 * Using `true` means: the related entity has no population of its own,
 * or we don't need to go deeper than one level.
 */
export type FooShape = {
    category: true;
    tags: true;
};


// ---------------------------------------------------------------------------
// 2. Nested Shape — a field references another entity's Shape type
// ---------------------------------------------------------------------------

import type { BarShape } from './BarShape.js';  // hypothetical
import type { BazShape } from './BazShape.js';  // hypothetical

/**
 * CompositeShape: demonstrates mixed leaf + nested fields.
 *
 * - `owner` is a leaf (the Owner entity has no populator, or we never go deeper)
 * - `bar` is nested: Bar itself has populatable fields (BarShape), so callers
 *   can request `{ bar: { relatedThing: true } }` to go two levels deep.
 * - `bazList` is a nested 1:many array where each Baz item is also populatable.
 */
export type CompositeShape = {
    owner: true;       // leaf — Owner has no further population
    bar: BarShape;     // nested — Bar can be further populated
    bazList: BazShape; // nested array — each Baz can be further populated
};


// ---------------------------------------------------------------------------
// 3. Rules of thumb
// ---------------------------------------------------------------------------
//
// Use `true` when:
//   - The related entity has no Populator of its own, OR
//   - You never need to go deeper than one $lookup from this entity.
//
// Use `RelatedShape` when:
//   - The related entity already has (or will have) its own Populator, AND
//   - Callers might want to populate fields of the related entity too.
//
// Shape types never contain runtime logic — they are type-level descriptions
// consumed by `normalizePopulate()` from @workspace/lib.
