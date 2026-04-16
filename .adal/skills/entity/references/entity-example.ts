/**
 * REFERENCE: Complete annotated entity example.
 *
 * This file is NOT real production code — it is a reference template
 * showing every major pattern used in a domain entity.
 * Read it when the project has few or no existing entities to learn from.
 *
 * Covers:
 *   - Basic entity structure (props, constructor, getters)
 *   - Static create() factory
 *   - Optional slug with generation + sanitization
 *   - Soft delete via deleted_at (inherited from Entity base)
 *   - Audit trail (updated_at / updated_by)
 *   - Business methods returning Result (fallible) or void (infallible)
 *   - Maybe<T> for optional lookups inside the entity
 *   - Nested sub-entity using namespace pattern
 *   - toDTO() serialization
 *   - Value object usage instead of primitives
 */

// --- Imports ---
// External libs first, then internal (always .js extension on imports)
import { Entity, IEntity } from "@dav/lib";
import { Result, Maybe } from "@dav/lib/monad";
import { DateTime } from "luxon";
import { ObjectId } from "mongodb";
import slugify from "slugify";

// DTOs use ~/dto/ alias
import ICatalogo from "~/dto/ICatalogo.js";
// Value objects from ~/value_object/
import EmailAddress from "~/value_object/impl/EmailAddress.js";
// Related entities with relative import
import Operatore from "./Operatore.js";

// =============================================================================
// Props type — all internal domain types (ObjectId, DateTime, Value Objects)
// =============================================================================
type CatalogoProps = {
    name: string;
    description: string;
    slug: string;
    stato: "bozza" | "pubblicato";

    // DateTime<true> = timezone-aware. Use this for all timestamps.
    deleted_at: DateTime<true> | null;
    created_at: DateTime;
    updated_at: DateTime;
    updated_by: Operatore | null;

    // ObjectId references — store the ID, optionally also the populated entity
    owner_id: ObjectId;
    owner?: Operatore;

    // Value object instead of plain string
    contact_email: EmailAddress | null;

    // Nested sub-entity collection (see namespace below)
    sezioni: Catalogo.Sezione[];
};

// =============================================================================
// Entity class
// =============================================================================
class Catalogo extends Entity<CatalogoProps, ObjectId> implements IEntity<ObjectId> {
    // Constructor always calls super with a wrapped ID.
    // new ObjectId(id) is idempotent: works whether id is already an ObjectId, a hex string, or undefined.
    constructor(props: CatalogoProps, id?: ObjectId) {
        super(props, new ObjectId(id));
    }

    // --- Getters (read-only by default) ---
    get name() { return this.props.name; }
    get description() { return this.props.description; }
    get slug() { return this.props.slug; }
    get stato() { return this.props.stato; }
    get owner_id() { return this.props.owner_id; }
    get owner() { return this.props.owner; }
    get contact_email() { return this.props.contact_email; }
    get sezioni() { return this.props.sezioni; }
    get created_at() { return this.props.created_at; }
    get updated_at() { return this.props.updated_at; }
    // deleted_at is inherited from Entity base class — no need to define it here

    // --- Business methods ---

    // Fallible operation: returns Result so the caller can handle the error path
    pubblica(operatore: Operatore): Result<void, Error> {
        if (this.props.stato !== "bozza") {
            return Result.err(new Error("Può essere pubblicato solo se in bozza"));
        }
        this.props.stato = "pubblicato";
        this._updateAudit(operatore);
        return Result.ok(undefined);
    }

    // Infallible mutation: returns void
    aggiornaDescrizione(description: string, operatore: Operatore): void {
        this.props.description = description;
        this._updateAudit(operatore);
    }

    // Optional lookup inside the entity: returns Maybe<T>
    getSezione(id: ObjectId): Maybe<Catalogo.Sezione> {
        const s = this.props.sezioni.find(s => s._id.equals(id));
        return Maybe.maybe(s);
    }

    // Adding a nested sub-entity
    aggiungiSezione(props: { nome: string }, operatore: Operatore): Catalogo.Sezione {
        const sezione = Catalogo.Sezione.create({ nome: props.nome });
        this.props.sezioni.push(sezione);
        this._updateAudit(operatore);
        return sezione;
    }

    // Private helper for audit update (not part of public API)
    private _updateAudit(operatore: Operatore): void {
        this.props.updated_at = DateTime.now();
        this.props.updated_by = operatore;
    }

    // --- DTO serialization ---
    // Every DTO field must be covered here.
    // Key serialization rules:
    //   ObjectId  → .toHexString()
    //   DateTime  → .toISO()!  (the ! is safe after toISO on a valid DateTime)
    //   nullable  → ?? null
    //   nested    → .toDTO()
    //   arrays    → .map(x => x.toDTO())
    //   ValueObj  → .toDTO()  (if VO has it) or .toString() / .value
    toDTO(): ICatalogo {
        return {
            _id: this._id.toHexString(),
            name: this.props.name,
            description: this.props.description,
            slug: this.props.slug,
            stato: this.props.stato,
            deleted_at: this.deleted_at?.toISO() ?? null,
            created_at: this.props.created_at.toISO()!,
            updated_at: this.props.updated_at.toISO()!,
            owner_id: this.props.owner_id.toHexString(),
            contact_email: this.props.contact_email?.toDTO() ?? null,
            sezioni: this.props.sezioni.map(s => s.toDTO()),
        };
    }

    // --- Static factory ---
    // ALL props are optional — the caller provides what it knows, defaults fill the rest.
    // Never call `new Catalogo(...)` from outside — always go through create().
    static create(props: {
        name?: string;
        description?: string;
        slug?: string;
        stato?: "bozza" | "pubblicato";
        deleted_at?: DateTime<true> | null;
        created_at?: DateTime;
        updated_at?: DateTime;
        updated_by?: Operatore | null;
        owner_id: ObjectId;           // required (no sensible default)
        contact_email?: EmailAddress | null;
        sezioni?: Catalogo.Sezione[];
    }, id?: ObjectId) {
        const name = props.name ?? "";
        return new Catalogo({
            name,
            description: props.description ?? "",
            slug: props.slug ?? Catalogo.generateSlug(name),
            stato: props.stato ?? "bozza",
            deleted_at: props.deleted_at ?? null,
            created_at: props.created_at ?? DateTime.now(),
            updated_at: props.updated_at ?? DateTime.now(),
            updated_by: props.updated_by ?? null,
            owner_id: props.owner_id,
            contact_email: props.contact_email ?? null,
            sezioni: props.sezioni ?? [],
        }, id);
    }

    // --- Slug helpers ---
    static generateSlug(name: string): string {
        if (!name.trim()) return "";
        const normalized = slugify.default(name, {
            lower: true, strict: true, replacement: '-', trim: true,
        });
        return normalized
            .replace(/[^a-z0-9-_]/g, '')
            .replace(/-+/g, '-')
            .replace(/_+/g, '_')
            .replace(/^[-_]+|[-_]+$/g, '');
    }

    setSlug(slug: string): void {
        this.props.slug = slug.toLowerCase().trim()
            .replace(/[^a-z0-9-_]/g, '')
            .replace(/-+/g, '-')
            .replace(/_+/g, '_')
            .replace(/^[-_]+|[-_]+$/g, '');
    }
}

// =============================================================================
// Namespace: nested sub-entities that don't live as top-level entities
// =============================================================================
namespace Catalogo {
    export type SezioneProps = {
        nome: string;
        sort_order: number;
    };

    export class Sezione extends Entity<SezioneProps, ObjectId> {
        constructor(props: SezioneProps, id?: ObjectId) {
            super(props, new ObjectId(id));
        }

        get nome() { return this.props.nome; }
        get sort_order() { return this.props.sort_order; }

        toDTO(): ICatalogo.Sezione {
            return {
                _id: this._id.toHexString(),
                nome: this.props.nome,
                sort_order: this.props.sort_order,
            };
        }

        static create(props: { nome?: string; sort_order?: number }, id?: ObjectId) {
            return new Sezione({
                nome: props.nome ?? "",
                sort_order: props.sort_order ?? 0,
            }, id);
        }
    }
}

export default Catalogo;
