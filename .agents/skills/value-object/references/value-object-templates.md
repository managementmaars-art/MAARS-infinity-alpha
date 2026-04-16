# Value Object Templates

This reference offers a few compact patterns that the value-object skill can use when generating code.

## Scalar wrapper

```ts
// value_object/IUsername.ts
export default interface IUsername {
  value: string;
}

// value_object/impl/Username.ts
import IUsername from "../IUsername.js";

export default class Username implements IUsername {
  public readonly value: string;

  private constructor(value: string) {
    this.value = value;
  }

  public static create(raw: string): Username {
    const trimmed = raw.trim();
    if (trimmed.length < 3 || trimmed.length > 30) {
      throw new Error("Username must be between 3 and 30 characters");
    }
    return new Username(trimmed);
  }

  public toRaw(): string {
    return this.value;
  }

  public toJSON(): IUsername {
    return { value: this.value };
  }
}
```

## Composite value object

```ts
// value_object/IAddress.ts
export default interface IAddress {
  street: string;
  city: string;
  postalCode: string;
  country: string;
}

// value_object/impl/Address.ts
import IAddress from "../IAddress.js";

export default class Address implements IAddress {
  public readonly street: string;
  public readonly city: string;
  public readonly postalCode: string;
  public readonly country: string;

  private constructor(raw: IAddress) {
    this.street = raw.street;
    this.city = raw.city;
    this.postalCode = raw.postalCode;
    this.country = raw.country;
  }

  public static create(raw: IAddress): Address {
    if (!raw.street || !raw.city) {
      throw new Error("Address must include street and city");
    }
    return new Address({
      street: raw.street.trim(),
      city: raw.city.trim(),
      postalCode: raw.postalCode.trim(),
      country: raw.country.trim(),
    });
  }

  public toRaw(): IAddress {
    return {
      street: this.street,
      city: this.city,
      postalCode: this.postalCode,
      country: this.country,
    };
  }
}
```

## Mapper pattern

```ts
// mapper/AddressMapper.ts
import Address from "../value_object/impl/Address.js";
import IAddress from "../value_object/IAddress.js";

export default class AddressMapper {
  public static fromRaw(raw: IAddress): Address {
    return Address.create(raw);
  }

  public static toRaw(address: Address): IAddress {
    return address.toRaw();
  }
}
```

## Notes

- Use a separate `mapper/` file only when the request describes persistence, database documents, or transport payloads.
- If the value object is a simple wrapper around a primitive, a dedicated interface and `toRaw()`/`fromRaw()` are usually enough.
- Keep the model focused on immutability and clear conversion boundaries.
