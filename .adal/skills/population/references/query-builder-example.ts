/**
 * QueryBuilder example for the population skill.
 *
 * Each entity that supports population gets its own QueryBuilder subclass.
 * The subclass's only job is to wire the entity's Shape + Populator into the
 * base QueryBuilder via a single `populateWith()` method.
 *
 * WORKSPACE NOTE: Replace `@workspace/lib` with your project's lib package name.
 * Replace `~/` path alias with whatever alias your tsconfig defines.
 */

import { normalizePopulate, type Populate } from '@workspace/lib';
import type FooDocument from '~/db/Documents/FooDocument.js';
import FooPopulator from '../populate/FooPopulator.js';
import type { FooShape } from '../shape/FooShape.js';
import QueryBuilder from './QueryBuilder.js';   // the shared base class

/**
 * FooQueryBuilder — builds MongoDB aggregation pipelines for the Foo collection.
 *
 * Usage:
 *   const pipeline = new FooQueryBuilder()
 *     .match({ deleted_at: null })
 *     .sort({ name: 1 })
 *     .page(pageNumber, pageSize)
 *     .populateWith({ category: true })          // only load category
 *     .populateWith('*')                         // load all fields
 *     .populateWith(['category', 'tags'])        // load by array
 *     .build();
 *
 * NOTE: populateWith() must come AFTER match/sort/page in the chain because
 * the base QueryBuilder appends $lookup stages at the end of the pipeline,
 * after $match/$sort/$skip/$limit — which is the correct MongoDB order for
 * performance (filter and paginate before joining).
 */
export default class FooQueryBuilder extends QueryBuilder<FooDocument> {
    /**
     * @param fields - Populate spec: object, array, `'*'`, or undefined/empty.
     *   Passing nothing or `{}` produces no $lookup stages.
     *   The `Populate<FooShape>` type from @workspace/lib accepts multiple formats:
     *     { category: true }
     *     ['category', 'tags']
     *     '*'
     *     { bar: { nestedField: true } }  // nested shape
     */
    populateWith(fields: Populate<FooShape> = {}): this {
        // normalizePopulate converts any input format into a uniform object
        // and validates against the shape definition (unknown keys become false).
        const normalized = normalizePopulate(fields, FooPopulator.SHAPE);
        const pipeline = FooPopulator.buildPipeline(normalized);
        this.push_populate_pipeline(pipeline);
        return this;
    }
}
