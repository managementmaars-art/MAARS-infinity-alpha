/**
 * Flat (leaf) Populator example for the population skill.
 *
 * This populator handles an entity whose populatable fields do NOT require
 * further nesting — all Shape fields are `true` (leaf nodes).
 *
 * Covers:
 *   - 1:1 relationship (Foo stores `bar_id` → load single Bar)
 *   - 1:many via reverse FK (Bar stores `foo_id` → load array of Bars)
 *   - 1:many via array of IDs (Foo stores `tag_ids[]` → load array of Tags)
 *   - Optional FK (`bar_id` can be null → preserve null with empty arrays)
 *
 * WORKSPACE NOTE: Replace `@workspace/lib` with your project's lib package.
 */

import { BasePopulator, type NormalizedPopulate } from '@workspace/lib';
import CollectionNameEnum from '~/db/CollectionNameEnum.js';
import type TCollectionName from '~/db/TCollectionName.js';
import type { FooShape } from '../shape/FooShape.js';

export default class FooPopulator extends BasePopulator<FooShape, TCollectionName> {
    /**
     * Static shape definition — must match the FooShape type exactly.
     * Used by `normalizePopulate()` to validate caller input and fill defaults.
     */
    static readonly SHAPE: FooShape = {
        category: true,   // 1:1, required FK
        tags: true,       // 1:many, reverse FK on Tag
        fileIds: true,    // 1:many, array of IDs stored on Foo
        owner: true,      // 1:1, nullable FK
    };

    // ------------------------------------------------------------------
    // Example 1: 1:1, non-nullable FK
    // Foo document has `category_id: ObjectId` pointing to Category.
    // ------------------------------------------------------------------
    private category(): void {
        if (!this.markPopulated('category')) return;  // guard: prevent duplicates
        this.addStages(
            this.lookup({
                from: CollectionNameEnum.category,
                localField: 'category_id',  // FK field on the Foo document
                foreignField: '_id',
                as: 'category',
            }),
            this.unwind('category'),  // flatten array → single object (1:1)
        );
    }

    // ------------------------------------------------------------------
    // Example 2: 1:many via reverse FK
    // Tag document has `foo_id: ObjectId`; Foo has no array field of its own.
    // ------------------------------------------------------------------
    private tags(): void {
        if (!this.markPopulated('tags')) return;
        this.addStages(
            this.lookup({
                from: CollectionNameEnum.tag,
                localField: '_id',     // Foo's own _id
                foreignField: 'foo_id', // FK stored on Tag documents
                as: 'tags',
            }),
            // No unwind — keeps the resulting array as-is
        );
    }

    // ------------------------------------------------------------------
    // Example 3: 1:many via array of IDs stored on Foo
    // Foo document has `file_ids: ObjectId[]`.
    // $lookup with an array localField matches any document whose _id is in the array.
    // ------------------------------------------------------------------
    private fileIds(): void {
        if (!this.markPopulated('fileIds')) return;
        this.addStages(
            this.lookup({
                from: CollectionNameEnum.file,
                localField: 'file_ids',  // array field on Foo
                foreignField: '_id',
                as: 'files',             // result field name (can differ from shape key)
            }),
            // No unwind — keeps array
        );
    }

    // ------------------------------------------------------------------
    // Example 4: 1:1, NULLABLE FK (owner_id can be null)
    // Without `preserveNullAndEmptyArrays`, unwind would drop documents
    // where the FK is null (empty $lookup result).
    // ------------------------------------------------------------------
    private owner(): void {
        if (!this.markPopulated('owner')) return;
        this.addStages(
            this.lookup({
                from: CollectionNameEnum.user,
                localField: 'owner_id',
                foreignField: '_id',
                as: 'owner',
            }),
            // preserve: true keeps the document even when owner_id is null
            this.unwind('owner', { preserveNullAndEmptyArrays: true }),
        );
    }

    /**
     * populate() is called with the normalized spec.
     * Each `if (spec.X)` guard checks whether the caller requested that field.
     */
    populate(spec: NormalizedPopulate<FooShape>): this {
        if (spec.category) this.category();
        if (spec.tags) this.tags();
        if (spec.fileIds) this.fileIds();
        if (spec.owner) this.owner();
        return this;
    }

    /**
     * Static helper — lets QueryBuilder (and tests) call buildPipeline()
     * without instantiating the populator manually.
     */
    static buildPipeline(spec: NormalizedPopulate<FooShape>): import('mongodb').Document[] {
        return new FooPopulator().populate(spec).build();
    }
}
