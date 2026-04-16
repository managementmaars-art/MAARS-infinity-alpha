/**
 * Nested Populator example for the population skill.
 *
 * Use this pattern when a populated field's entity ALSO has populatable fields —
 * e.g., loading a Foo that references a Bar, and Bar can itself be populated
 * with a Baz. MongoDB supports this via the `pipeline` option of $lookup.
 *
 * The key differences from a flat populator:
 *   - Shape fields that can nest use `BarShape` instead of `true`
 *   - `populate()` receives `spec.bar` as `NormalizedPopulate<BarShape>` (not boolean)
 *   - Each nested private method accepts the sub-spec and calls sub-populator
 *
 * WORKSPACE NOTE: Replace `@workspace/lib` with your project's lib package.
 */

import { BasePopulator, type NormalizedPopulate } from '@workspace/lib';
import CollectionNameEnum from '~/db/CollectionNameEnum.js';
import type TCollectionName from '~/db/TCollectionName.js';
import type { FooShape } from '../shape/FooShape.js';
import type { BarShape } from '../shape/BarShape.js';
import type { BazShape } from '../shape/BazShape.js';
import BarPopulator from './BarPopulator.js';
import BazPopulator from './BazPopulator.js';

export default class FooPopulator extends BasePopulator<FooShape, TCollectionName> {
    static readonly SHAPE: FooShape = {
        // `true` — simple leaf: the related entity has no further population
        label: true,
        // `BarPopulator.SHAPE` — nested: Bar can itself be populated further
        bar: BarPopulator.SHAPE,
        // `BazPopulator.SHAPE` — nested 1:many array: each Baz is also populatable
        bazList: BazPopulator.SHAPE,
    };

    // ------------------------------------------------------------------
    // Simple leaf field (no nesting)
    // ------------------------------------------------------------------
    private label(): void {
        if (!this.markPopulated('label')) return;
        this.addStages(
            this.lookup({
                from: CollectionNameEnum.label,
                localField: 'label_id',
                foreignField: '_id',
                as: 'label',
            }),
            this.unwind('label'),
        );
    }

    // ------------------------------------------------------------------
    // Nested 1:1 — Bar itself may be further populated.
    // The sub-pipeline is built by BarPopulator and passed into $lookup.
    // ------------------------------------------------------------------
    private bar(nestedSpec: NormalizedPopulate<BarShape>): void {
        if (!this.markPopulated('bar')) return;

        // Build Bar's own aggregation pipeline based on what the caller requested.
        // If nestedSpec is empty (all false), this returns [], which is fine —
        // $lookup with an empty pipeline just does a plain join.
        const nestedPipeline = BarPopulator.buildPipeline(nestedSpec);

        this.addStages(
            this.lookup({
                from: CollectionNameEnum.bar,
                localField: 'bar_id',
                foreignField: '_id',
                as: 'bar',
                pipeline: nestedPipeline,  // <-- nested population magic
            }),
            this.unwind('bar'),            // 1:1 — unwrap the single-element array
        );
    }

    // ------------------------------------------------------------------
    // Nested 1:many array — each Baz in the result array can be populated.
    // ------------------------------------------------------------------
    private bazList(nestedSpec: NormalizedPopulate<BazShape>): void {
        if (!this.markPopulated('bazList')) return;

        const nestedPipeline = BazPopulator.buildPipeline(nestedSpec);

        this.addStages(
            this.lookup({
                from: CollectionNameEnum.baz,
                localField: '_id',         // Foo._id
                foreignField: 'foo_id',    // Baz.foo_id (reverse FK)
                as: 'bazList',
                pipeline: nestedPipeline,
            }),
            // No unwind — keep the array
        );
    }

    /**
     * populate() dispatches to each private method.
     *
     * For leaf fields: spec.label is a boolean (true | false)
     * For nested fields: spec.bar is a NormalizedPopulate<BarShape> object,
     *   which is truthy when the field was requested. Pass it directly to the
     *   private method so it can forward it to the sub-populator.
     */
    populate(spec: NormalizedPopulate<FooShape>): this {
        if (spec.label) this.label();
        if (spec.bar) this.bar(spec.bar);           // spec.bar is NormalizedPopulate<BarShape>
        if (spec.bazList) this.bazList(spec.bazList); // spec.bazList is NormalizedPopulate<BazShape>
        return this;
    }

    static buildPipeline(spec: NormalizedPopulate<FooShape>): import('mongodb').Document[] {
        return new FooPopulator().populate(spec).build();
    }
}

// ---------------------------------------------------------------------------
// Caller example — what a repository method looks like when using this:
// ---------------------------------------------------------------------------
//
//   const pipeline = new FooQueryBuilder()
//     .match({ status: 'active' })
//     .populateWith({
//         label: true,
//         bar: {                          // request nested population of Bar
//             relatedThing: true,         // populate Bar's own `relatedThing` field
//         },
//         bazList: '*',                   // populate all fields on each Baz
//     })
//     .build();
//
//   const docs = await coll.aggregate<FooDocument>(pipeline).toArray();
//   return docs.map(FooMapper.from);
