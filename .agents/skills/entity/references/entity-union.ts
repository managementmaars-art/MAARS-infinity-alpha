// =============================================================================
// src/entity/Elemento.ts  — union + discriminant-extraction utility
// =============================================================================

import ElementoDinamico from './ElementoDinamico.js';
import ElementoTesto from './ElementoTesto.js';

type Elemento = ElementoTesto | ElementoDinamico;

// Extracts the concrete subtype from its 'type' discriminant literal.
export type ExtractElementoFromType<T extends Elemento['type']> =
    T extends 'TEXT'    ? ElementoTesto    :
    T extends 'DYNAMIC' ? ElementoDinamico :
    never;

export default Elemento;


// =============================================================================
// src/entity/ElementoBase.ts  — shared base for all Elemento subtypes
// =============================================================================

import { Entity } from '@workspace/lib';
import { ObjectId } from 'mongodb';
import IElementoBase from '~/dto/IElementoBase.js';

export type ElementoBaseProps = {
    name: string;
    description: string;
};

export default abstract class ElementoBase<P extends ElementoBaseProps = ElementoBaseProps>
    extends Entity<P, ObjectId> {

    constructor(props: P, id?: ObjectId) {
        super(props, new ObjectId(id));
    }

    // Each subclass must declare its own `public readonly type` literal —
    // that field is the discriminant that makes the union narrowable.
    abstract readonly type: string;

    get name() { return this.props.name; }
    get description() { return this.props.description; }

    toDTO(): IElementoBase {
        return {
            _id: this._id.toHexString(),
            name: this.props.name,
            description: this.props.description,
        };
    }
}


// =============================================================================
// src/entity/ElementoTesto.ts  — simple subtype with no extra props
// =============================================================================

import { ObjectId } from 'mongodb';
import IElementoTesto from '~/dto/IElementoTesto.js';
import ElementoBase, { ElementoBaseProps } from './ElementoBase.js';

export interface TestoProps extends ElementoBaseProps {
    content: string;
}

export default class ElementoTesto extends ElementoBase<TestoProps> {
    public readonly type = 'TEXT';

    get content() { return this.props.content; }

    override toDTO(): IElementoTesto {
        return {
            ...super.toDTO(),
            type: this.type,
            content: this.props.content,
        };
    }

    static create(props: { name?: string; description?: string; content?: string }, id?: ObjectId) {
        return new ElementoTesto(
            {
                name: props.name ?? '',
                description: props.description ?? '',
                content: props.content ?? '',
            },
            id,
        );
    }
}


// =============================================================================
// src/entity/ElementoDinamico.ts  — subtype with additional props and methods
// =============================================================================

import { ObjectId } from 'mongodb';
import IElementoDinamico from '~/dto/IElementoDinamico.js';
import ElementoBase, { ElementoBaseProps } from './ElementoBase.js';

export interface DinamicoProps extends ElementoBaseProps {
    vector_id: ObjectId | null;
    size: number;
}

export default class ElementoDinamico extends ElementoBase<DinamicoProps> {
    public readonly type = 'DYNAMIC';

    get vector_id() { return this.props.vector_id; }
    get size() { return this.props.size; }

    // Subtype-specific mutation method
    setVectorId(vector_id: ObjectId | null) {
        this.props.vector_id = vector_id;
    }

    override toDTO(): IElementoDinamico {
        return {
            ...super.toDTO(),
            type: this.type,
            vector_id: this.props.vector_id?.toHexString() ?? null,
            size: this.props.size,
        };
    }

    static create(
        props: { name?: string; description?: string; vector_id?: ObjectId | null; size?: number },
        id?: ObjectId,
    ) {
        return new ElementoDinamico(
            {
                name: props.name ?? '',
                description: props.description ?? '',
                vector_id: props.vector_id ?? null,
                size: props.size ?? 0,
            },
            id,
        );
    }
}
