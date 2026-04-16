/**
 * Aggregate Repository Example — aggregation pipeline, optional population, streaming, bulk save.
 *
 * Use this pattern when:
 *   - Callers need related entities eagerly loaded (the "populate" option)
 *   - Complex filtering that benefits from $match aggregation stages
 *   - Large result sets that should be streamed rather than loaded in full
 *   - Bulk writes via saveMany()
 *
 * The QueryBuilder and population system (Shape, Populator, QueryBuilder files) are a separate
 * concern handled by a dedicated skill. This example shows how the repo *uses* them.
 * If those files don't exist yet for this entity, they need to be created separately.
 *
 * Replace `@workspace/lib` with the actual shared lib package name (e.g. @dav/lib, @myapp/lib).
 * Replace `Foo`/`foo`/`Bar` with the real entity names throughout.
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// DOCUMENT — src/db/Documents/FooDocument.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { ObjectId } from "mongodb";
import IFoo from "~/dto/IFoo.js";
import BarDocument from "./BarDocument.js";
import TagDocument from "./TagDocument.js";

// When some DTO fields are computed and never stored, Omit them before Overwrite.
// Here "display_tags" is a computed view that the DTO exposes but MongoDB doesn't store.
type FooDocument = Overwrite<
    Omit<IFoo, "display_tags">,
    {
        _id: ObjectId;
        deleted_at: Date | null;
        category_id: ObjectId | null;   // FK stored as ObjectId (DTO has string)
        bar?: BarDocument | null;        // optional — only present after $lookup aggregation
        tags?: TagDocument[];            // optional array — only present after $lookup aggregation
    }
>;

export default FooDocument;


// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// INTERFACE — src/repo/IFooRepo.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { Maybe } from "@workspace/lib/monad";
import type { Populate } from "@workspace/lib";
import { ObjectId } from "mongodb";
import { Readable } from "node:stream";
import Foo from "~/entity/Foo.js";
import type { FooShape } from "./shape/FooShape.js"; // from the population system

export type SearchFoo = {
    name?: string;
    include_deleted?: boolean;
};

// The options parameter with populate? is the hook for the population system.
// All read methods that should support eager-loading accept it.
interface IFooRepo {
    search(query: SearchFoo, options?: IFooRepo.Options): Promise<Foo[]>;
    searchStream(query: SearchFoo, options?: IFooRepo.Options): Readable;
    get(id: ObjectId, options?: IFooRepo.Options): Promise<Maybe<Foo>>;
    findByIds(ids: ObjectId[], options?: IFooRepo.Options): Promise<Foo[]>;
    findBySlug(slug: string, options?: IFooRepo.Options): Promise<Maybe<Foo>>;
    save(entity: Foo): Promise<void>;
    saveMany(entities: Foo[]): Promise<void>;
}

namespace IFooRepo {
    export type Options = {
        // Populate<FooShape> is a partial of the shape — callers specify only what they need.
        // When undefined, no $lookup stages are added to the pipeline.
        populate?: Populate<FooShape>;
    };
}

export default IFooRepo;


// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// IMPLEMENTATION — src/repo/impl/FooRepoImpl.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { Maybe } from "@workspace/lib/monad";
import { inject, injectable } from "inversify";
import { Collection, Filter, ObjectId } from "mongodb";
import { Readable } from "node:stream";
import type IDatabaseContext from "~/db/Context/IDatabaseContext.js";
import FooDocument from "~/db/Documents/FooDocument.js";
import prepareBulkOps from "~/db/prepareBulkOps.js";
import Symbols from "~/di/Symbols.js";
import Foo from "~/entity/Foo.js";
import FooMapper from "~/mapper/FooMapper.js";
import IFooRepo, { SearchFoo } from "../IFooRepo.js";
import FooQueryBuilder from "../query/FooQueryBuilder.js"; // part of the population system

@injectable()
export default class FooRepoImpl implements IFooRepo {
    constructor(
        @inject(Symbols.Collections.foo) private readonly coll: Collection<FooDocument>,
        @inject(Symbols.DatabaseContext) private readonly db: IDatabaseContext,
    ) {}

    // ── Read operations ───────────────────────────────────────────────────

    async search(query: SearchFoo, options?: IFooRepo.Options): Promise<Foo[]> {
        const filter: Filter<FooDocument> = {};
        if (query.name) filter.name = new RegExp(`^${query.name}`, "i");
        if (!query.include_deleted) filter.deleted_at = null;

        // QueryBuilder builds a $match → (optional populate stages) → $sort pipeline.
        // populateWith(undefined) is a no-op — the query runs cleanly without $lookup stages.
        const pipeline = new FooQueryBuilder()
            .match(filter)
            .populateWith(options?.populate)
            .sort({ name: 1 })
            .build();

        const docs = await this.coll
            .aggregate<FooDocument>(pipeline, { session: this.db.session })
            .toArray();
        return docs.map(FooMapper.from);
    }

    searchStream(query: SearchFoo, options?: IFooRepo.Options): Readable {
        // Stream large result sets instead of loading everything into memory with .toArray().
        // The cursor is closed when the stream ends or errors.
        const filter: Filter<FooDocument> = {};
        if (query.name) filter.name = new RegExp(`^${query.name}`, "i");
        if (!query.include_deleted) filter.deleted_at = null;

        const pipeline = new FooQueryBuilder()
            .match(filter)
            .populateWith(options?.populate)
            .sort({ name: 1 })
            .build();

        const cursor = this.coll.aggregate<FooDocument>(pipeline, { session: this.db.session });
        let isDestroyed = false;

        return new Readable({
            objectMode: true,       // push entity objects, not Buffers
            async read() {
                if (isDestroyed) return;
                try {
                    const hasNext = await cursor.hasNext();
                    if (hasNext) {
                        const doc = await cursor.next();
                        if (doc) this.push(FooMapper.from(doc));
                    } else {
                        this.push(null); // signals end of stream
                        await cursor.close();
                    }
                } catch (error) {
                    this.destroy(error instanceof Error ? error : new Error("Stream read error"));
                }
            },
            async destroy(error, callback) {
                isDestroyed = true;
                try {
                    await cursor.close();
                    callback(error);
                } catch (closeError) {
                    callback((closeError instanceof Error ? closeError : new Error("Cursor close error")) || error);
                }
            },
        });
    }

    async get(id: ObjectId, options?: IFooRepo.Options): Promise<Maybe<Foo>> {
        // Using aggregate + limit(1) instead of findOne so that populate stages can apply.
        const pipeline = new FooQueryBuilder()
            .match({ _id: id } as Filter<FooDocument>)
            .populateWith(options?.populate)
            .limit(1)
            .build();

        const docs = await this.coll
            .aggregate<FooDocument>(pipeline, { session: this.db.session })
            .toArray();

        if (!docs.length) return Maybe.none();
        return Maybe.maybe(FooMapper.from(docs[0]!));
    }

    async findByIds(ids: ObjectId[], options?: IFooRepo.Options): Promise<Foo[]> {
        // Short-circuit for empty input — avoids an unnecessary database round-trip.
        if (!ids.length) return [];

        const pipeline = new FooQueryBuilder()
            .match({ _id: { $in: ids } })
            .populateWith(options?.populate)
            .build();

        const docs = await this.coll
            .aggregate<FooDocument>(pipeline, { session: this.db.session })
            .toArray();
        return docs.map(FooMapper.from);
    }

    async findBySlug(slug: string, options?: IFooRepo.Options): Promise<Maybe<Foo>> {
        const pipeline = new FooQueryBuilder()
            .match({ slug })
            .populateWith(options?.populate)
            .limit(1)
            .build();

        const docs = await this.coll
            .aggregate<FooDocument>(pipeline, { session: this.db.session })
            .toArray();

        if (!docs.length) return Maybe.none();
        return Maybe.maybe(FooMapper.from(docs[0]!));
    }

    // ── Write operations ──────────────────────────────────────────────────

    async save(entity: Foo): Promise<void> {
        const raw = FooMapper.to(entity);

        if (entity.isDeleted()) {
            // Soft-delete: mark the record without removing it.
            await this.coll.updateOne(
                { _id: raw._id },
                { $set: { deleted_at: entity.deleted_at!.toJSDate() } },
                { session: this.db.session },
            );
        } else {
            await this.coll.updateOne(
                { _id: raw._id },
                { $set: raw },
                { upsert: true, session: this.db.session },
            );
        }
    }

    async saveMany(entities: Foo[]): Promise<void> {
        // prepareBulkOps produces deleteOne / updateOne($set, upsert) operations
        // based on entity.isDeleted() — same logic as save() but in a single bulkWrite.
        const ops = prepareBulkOps(entities, FooMapper);
        if (!ops.length) return; // guard against empty arrays from the driver
        await this.coll.bulkWrite(ops, { session: this.db.session });
    }
}


// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MAPPER — src/mapper/FooMapper.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { IEntityMapper } from "@workspace/lib";
import { DateTime } from "luxon";
import FooDocument from "~/db/Documents/FooDocument.js";
import Foo from "~/entity/Foo.js";
import BarMapper from "./BarMapper.js";
import TagMapper from "./TagMapper.js";

const FooMapper: IEntityMapper<Foo, FooDocument> = {
    /**
     * from: document → entity (read path).
     *
     * Two-step construction:
     *   1. Build the entity with own stored fields (always present on any document).
     *   2. Patch in populated sub-documents — only present when a $lookup pipeline ran.
     *
     * This asymmetry is intentional: a document without $lookup stages is valid and common.
     * The entity's default values (null, []) cover the no-populate case cleanly.
     */
    from: (doc: FooDocument): Foo => {
        const entity = new Foo({
            name: doc.name,
            category_id: doc.category_id,
            deleted_at: doc.deleted_at
                ? DateTime.fromJSDate(doc.deleted_at) as DateTime<true>
                : null,
            bar: null,      // default — overwritten below if the pipeline joined it
            tags: [],       // default — overwritten below if the pipeline joined them
        }, doc._id);

        // Optional populated sub-documents — check for presence before mapping.
        if (doc.bar) entity.props.bar = BarMapper.from(doc.bar);
        if (doc.tags) entity.props.tags = doc.tags.map(TagMapper.from);

        return entity;
    },

    /**
     * to: entity → document (write path).
     *
     * Only serializes own stored scalar fields and FK ObjectIds.
     * Populated relations (bar, tags) are never written back — they come from separate collections.
     * Writing them would create data duplication and break referential integrity.
     */
    to: (domain: Foo): FooDocument => ({
        _id: domain._id,
        name: domain.props.name,
        category_id: domain.props.category_id,
        deleted_at: domain.deleted_at?.toJSDate() ?? null,
        // No bar, no tags — those live in their own collections.
    }),
};

export default FooMapper;
