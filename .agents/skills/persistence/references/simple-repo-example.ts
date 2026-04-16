/**
 * Simple Repository Example — no population, uses find/findOne.
 *
 * Use this pattern when:
 *   - The entity doesn't need related entities eagerly loaded
 *   - Queries are simple filter + sort (no aggregation stages or $lookup needed)
 *
 * This file contains all four persistence files in one place for reference.
 * In the real project, each section goes in its own file as noted.
 *
 * Replace `@workspace/lib` with the actual shared lib package name (e.g. @dav/lib, @myapp/lib).
 * Replace `Foo`/`foo` with the real entity name throughout.
 */

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// DOCUMENT — src/db/Documents/FooDocument.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { ObjectId } from "mongodb";
import IFoo from "~/dto/IFoo.js";

// Overwrite overrides specific fields of the DTO with their MongoDB equivalents.
// Only list fields that differ — everything else is inherited from IFoo as-is.
type FooDocument = Overwrite<IFoo, {
    _id: ObjectId;              // DTO: string → Document: ObjectId
    created_at: Date;           // DTO: string (ISO) → Document: JS Date
    deleted_at: Date | null;    // null when not deleted; non-null when soft-deleted
    owner_id: ObjectId | null;  // FK: DTO has string → Document has ObjectId
}>;

export default FooDocument;


// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// INTERFACE — src/repo/IFooRepo.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { Maybe } from "@workspace/lib/monad";
import { ObjectId } from "mongodb";
import Foo from "~/entity/Foo.js";

// Export the search query type alongside the interface so callers can import both.
// Optional fields let callers specify only what they care about.
export type SearchFoo = {
    name?: string;              // prefix match, case-insensitive
    include_deleted?: boolean;  // when false (default), soft-deleted records are excluded
};

interface IFooRepo {
    search(query: SearchFoo): Promise<Foo[]>;          // empty array when nothing matches — never Maybe
    get(id: ObjectId): Promise<Maybe<Foo>>;            // Maybe.none() when not found
    getByEmail(email: string): Promise<Maybe<Foo>>;    // example: alternative lookup key
    count(): Promise<number>;                          // example: count active records
    save(entity: Foo): Promise<void>;
}

export default IFooRepo;


// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// IMPLEMENTATION — src/repo/impl/FooRepoImpl.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
        // Injected as Collection<FooDocument> — typed by the ICollectionsDocument mapping.
        // The symbol key must match the collection name string exactly.
        @inject(Symbols.Collections.foo) private readonly coll: Collection<FooDocument>,
        // IDatabaseContext carries the current MongoDB ClientSession.
        // It is undefined when no transaction is active; the driver ignores undefined sessions.
        @inject(Symbols.DatabaseContext) private readonly db: IDatabaseContext,
    ) {}

    async search(query: SearchFoo): Promise<Foo[]> {
        const filter: Filter<FooDocument> = {};
        if (query.name) filter.name = new RegExp(`^${query.name}`, "i");
        if (!query.include_deleted) filter.deleted_at = null;

        const docs = await this.coll
            // Pass session on every call — this wires the operation into any active transaction.
            // Without it the call runs outside the transaction and can't be rolled back.
            .find(filter, { session: this.db.session })
            .sort({ name: 1 })
            .toArray();
        return docs.map(FooMapper.from);
    }

    async get(id: ObjectId): Promise<Maybe<Foo>> {
        const doc = await this.coll.findOne({ _id: id }, { session: this.db.session });
        // Maybe.maybe(null) → Maybe.none(); Maybe.maybe(doc) → Maybe.some(doc)
        return Maybe.maybe(doc).map(FooMapper.from);
    }

    async getByEmail(email: string): Promise<Maybe<Foo>> {
        // Nested field access: "email.address" for embedded value objects
        const doc = await this.coll.findOne(
            { "email.address": email },
            { session: this.db.session },
        );
        return Maybe.maybe(doc).map(FooMapper.from);
    }

    async count(): Promise<number> {
        return this.coll.countDocuments({ deleted_at: null }, { session: this.db.session });
    }

    async save(entity: Foo): Promise<void> {
        const raw = FooMapper.to(entity);

        if (entity.isDeleted()) {
            // Soft-delete: keep the document but mark deleted_at.
            // Only set deleted_at — don't overwrite other fields to avoid race conditions.
            await this.coll.updateOne(
                { _id: raw._id },
                { $set: { deleted_at: entity.deleted_at!.toJSDate() } },
                { session: this.db.session },
            );
        } else {
            // Upsert: insert if new, replace fields if existing.
            await this.coll.updateOne(
                { _id: raw._id },
                { $set: raw },
                { upsert: true, session: this.db.session },
            );
        }
    }
}


// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MAPPER — src/mapper/FooMapper.ts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { IEntityMapper } from "@workspace/lib";
import { DateTime } from "luxon";
import FooDocument from "~/db/Documents/FooDocument.js";
import Foo from "~/entity/Foo.js";

const FooMapper: IEntityMapper<Foo, FooDocument> = {
    /**
     * from: document → entity (read path).
     * Converts MongoDB types (ObjectId, Date) to domain types.
     * Called after every database read.
     *
     * Note: uses Foo.create() here because this entity has defaults worth preserving.
     * Some projects use `new Foo(props, id)` directly in mappers — check existing mappers and match.
     */
    from: (doc: FooDocument): Foo => {
        return Foo.create({
            name: doc.name,
            owner_id: doc.owner_id,    // ObjectId passes through as-is (entity stores ObjectId)
            created_at: doc.created_at
                ? DateTime.fromJSDate(doc.created_at) as DateTime<true>
                : undefined,
            deleted_at: doc.deleted_at
                ? DateTime.fromJSDate(doc.deleted_at) as DateTime<true>
                : null,
        }, doc._id);
    },

    /**
     * to: entity → document (write path).
     * Serializes only own stored scalar fields and FK ObjectIds.
     * Never include populated join results — they are read-only aggregation outputs.
     */
    to: (domain: Foo): FooDocument => ({
        _id: domain._id,
        name: domain.props.name,
        owner_id: domain.props.owner_id,
        created_at: domain.props.created_at?.toJSDate(),
        deleted_at: domain.deleted_at?.toJSDate() ?? null,
    }),
};

export default FooMapper;
