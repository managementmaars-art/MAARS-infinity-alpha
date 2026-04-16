/**
 * REFERENCE: Complete annotated DTO example.
 *
 * This file is NOT real production code — it is a reference template.
 * Read it when the project has few or no existing DTOs to learn from.
 *
 * Covers:
 *   - Basic DTO structure (interface, snake_case, _id: string)
 *   - Namespace for enums, union types, sub-interfaces
 *   - Discriminated union pattern (polymorphic entities)
 *   - Optional populated relations vs. required reference IDs
 *   - Nullable DateTime fields (serialized as string)
 *   - Mutually exclusive actor pattern
 */

// =============================================================================
// Basic DTO — mirrors the entity's public data, no methods
// =============================================================================
interface ICatalogo {
    _id: string;                    // always string (not ObjectId)
    name: string;
    description: string;
    slug: string;
    stato: ICatalogo.Stato;         // use namespaced type for enums

    // DateTime fields: serialized as ISO string
    created_at: string;
    updated_at: string;
    deleted_at: string | null;      // nullable DateTime → string | null

    // Foreign key reference: always include the ID
    owner_id: string;
    // Populated relation: optional, only present when explicitly loaded
    owner?: IOperatore;

    contact_email: IEmailAddress | null;

    sezioni: ICatalogo.Sezione[];
}

namespace ICatalogo {
    // --- Enums as string literal unions ---
    export type Stato = "bozza" | "pubblicato";

    // --- Nested sub-interface ---
    export interface Sezione {
        _id: string;
        nome: string;
        sort_order: number;
        // Self-reference for tree structures:
        // parent_id: string | null;
        // children?: Sezione[];
    }

    // --- Utility type extraction ---
    export type StatoType = Stato; // re-export for convenience if needed
}

export default ICatalogo;

// =============================================================================
// Discriminated union pattern — for entities that have multiple subtypes
// =============================================================================

// Base interface with shared fields
interface IElementoBase {
    _id: string;
    sku: string;
    name: string;
    deleted_at: string | null;
}

// Union type — caller narrows by checking `type`
type IElemento = IElemento.Testo | IElemento.Immagine;

namespace IElemento {
    export interface Testo extends IElementoBase {
        type: "TEXT";           // discriminator — must be a literal
        testo: {
            contenuto: string;
            font_size: number;
        };
        immagine?: never;       // explicitly exclude the other variant's field
    }

    export interface Immagine extends IElementoBase {
        type: "GRAPHIC";
        immagine: {
            url: string;
            width: number;
            height: number;
        };
        testo?: never;
    }

    // Useful utility type to extract discriminator values
    export type Type = IElemento["type"]; // "TEXT" | "GRAPHIC"
}

export type { IElemento };

// =============================================================================
// Mutually exclusive actor pattern — used in audit logs and auth contexts
// =============================================================================
namespace IEvento {
    interface IOperatoreActor {
        type: "OPERATORE";
        operatore: IOperatore;
        impresa?: never;        // `never` prevents mixing actor types
    }

    interface IImpresaActor {
        type: "IMPRESA";
        impresa: IImpresa;
        operatore?: never;
    }

    export type Attore = IOperatoreActor | IImpresaActor;
}

// =============================================================================
// Placeholder references for types used above
// (in a real project these would be proper imports)
// =============================================================================
interface IOperatore { _id: string; nome: string; }
interface IImpresa { _id: string; ragione_sociale: string; }
interface IEmailAddress { value: string; }
