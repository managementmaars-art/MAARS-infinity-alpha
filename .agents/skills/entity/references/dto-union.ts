// =============================================================================
// src/dto/IElemento.ts  — union type + discriminant-extraction utility
// =============================================================================

import IElementoTesto from './IElementoTesto.js';
import IElementoDinamico from './IElementoDinamico.js';

type IElemento = IElementoTesto | IElementoDinamico;

// Mirrors ExtractElementoFromType on the entity side — narrows to the DTO subtype.
export type ExtractIElementoFromType<T extends IElemento['type']> =
    T extends 'TEXT'    ? IElementoTesto    :
    T extends 'DYNAMIC' ? IElementoDinamico :
    never;

export default IElemento;


// =============================================================================
// src/dto/IElementoBase.ts  — shared fields for all Elemento subtypes
// =============================================================================

export default interface IElementoBase {
    _id: string;      // always string (serialized ObjectId)
    name: string;
    description: string;
}


// =============================================================================
// src/dto/IElementoTesto.ts  — simple subtype DTO
// =============================================================================

import IElementoBase from './IElementoBase.js';

export default interface IElementoTesto extends IElementoBase {
    type: 'TEXT';   // discriminant literal — must match entity's `readonly type`
    content: string;
}


// =============================================================================
// src/dto/IElementoDinamico.ts  — subtype DTO with additional fields
// =============================================================================

import IElementoBase from './IElementoBase.js';

export default interface IElementoDinamico extends IElementoBase {
    type: 'DYNAMIC';
    vector_id: string | null;   // ObjectId serialized to string (or null)
    size: number;
}
