# Pydantic v2 Migration Patterns

Migration guide from Pydantic v1 to v2. Use this reference when updating existing code or when encountering v1-style patterns.

---

## Key API Changes

### Configuration

```python
# v1 (deprecated)
class UserResponse(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# v2 (current)
from pydantic import ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,        # replaces orm_mode
        populate_by_name=True,       # replaces allow_population_by_field_name
        str_strip_whitespace=True,   # new in v2
    )
```

### Model Methods

| v1 (deprecated) | v2 (current) | Notes |
|-----------------|-------------|-------|
| `.from_orm(obj)` | `.model_validate(obj)` | Converts ORM model to Pydantic |
| `.dict()` | `.model_dump()` | Converts to dictionary |
| `.json()` | `.model_dump_json()` | Converts to JSON string |
| `.parse_obj(data)` | `.model_validate(data)` | Validates dict input |
| `.parse_raw(json_str)` | `.model_validate_json(json_str)` | Validates JSON string |
| `.schema()` | `.model_json_schema()` | Returns JSON Schema |
| `.construct()` | `.model_construct()` | Create without validation |
| `.copy(update={})` | `.model_copy(update={})` | Copy with updates |

### Field Definitions

```python
# v1 (deprecated)
from pydantic import Field

class User(BaseModel):
    name: str = Field(..., min_length=1)  # ... means required
    age: Optional[int] = None

# v2 (current)
class User(BaseModel):
    name: str = Field(min_length=1)       # required by default (no ...)
    age: int | None = None                # use | None instead of Optional
```

### Validators

```python
# v1 (deprecated)
from pydantic import validator, root_validator

class User(BaseModel):
    email: str

    @validator("email")
    @classmethod
    def validate_email(cls, v):
        return v.lower()

    @root_validator
    @classmethod
    def validate_model(cls, values):
        return values

# v2 (current)
from pydantic import field_validator, model_validator

class User(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower()

    @model_validator(mode="after")
    def validate_model(self) -> "User":
        # self is the fully constructed model
        return self
```

### Computed Fields (New in v2)

```python
from pydantic import computed_field

class OrderResponse(BaseModel):
    subtotal_cents: int
    tax_cents: int

    @computed_field
    @property
    def total_cents(self) -> int:
        return self.subtotal_cents + self.tax_cents
```

---

## Type Annotation Changes

```python
# v1 style
from typing import Optional, List, Dict

class User(BaseModel):
    tags: List[str] = []
    metadata: Dict[str, str] = {}
    nickname: Optional[str] = None

# v2 style (Python 3.12+)
class User(BaseModel):
    tags: list[str] = []
    metadata: dict[str, str] = {}
    nickname: str | None = None
```

---

## Strict Mode

Pydantic v2 introduces strict mode to prevent type coercion:

```python
from pydantic import BaseModel, ConfigDict

class StrictUser(BaseModel):
    model_config = ConfigDict(strict=True)

    age: int
    name: str

# Without strict: StrictUser(age="25", name="Alice") → age=25 (coerced)
# With strict: StrictUser(age="25", name="Alice") → ValidationError
```

Per-field strict mode:

```python
from pydantic import Field

class User(BaseModel):
    age: int = Field(strict=True)  # Only this field is strict
    name: str
```

---

## Discriminated Unions (Improved in v2)

```python
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Discriminator, Tag

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meow_volume: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    bark_volume: int

# v2 discriminated union
Pet = Annotated[
    Union[
        Annotated[Cat, Tag("cat")],
        Annotated[Dog, Tag("dog")],
    ],
    Discriminator("pet_type"),
]

class Owner(BaseModel):
    pet: Pet  # Automatically selects Cat or Dog based on pet_type
```

---

## Common Migration Patterns

### Pattern 1: ORM Model to Response

```python
# v1
response = UserResponse.from_orm(user_model)

# v2
response = UserResponse.model_validate(user_model)
```

### Pattern 2: Partial Update (PATCH)

```python
# v1
update_data = patch_schema.dict(exclude_unset=True)

# v2
update_data = patch_schema.model_dump(exclude_unset=True)
```

### Pattern 3: Response Serialization

```python
# v1
return user.dict(exclude={"hashed_password"})

# v2
return user.model_dump(exclude={"hashed_password"})
```

### Pattern 4: JSON Serialization

```python
# v1
json_str = user.json()
user = User.parse_raw(json_str)

# v2
json_str = user.model_dump_json()
user = User.model_validate_json(json_str)
```

### Pattern 5: Schema Copy with Update

```python
# v1
updated = user.copy(update={"name": "New Name"})

# v2
updated = user.model_copy(update={"name": "New Name"})
```

---

## Deprecated Features to Remove

| Deprecated | Action |
|-----------|--------|
| `class Config:` | Replace with `model_config = ConfigDict(...)` |
| `orm_mode = True` | Replace with `from_attributes=True` |
| `@validator` | Replace with `@field_validator` |
| `@root_validator` | Replace with `@model_validator` |
| `Optional[X]` | Replace with `X \| None` |
| `List[X]` | Replace with `list[X]` |
| `Dict[K, V]` | Replace with `dict[K, V]` |
| `Tuple[X, ...]` | Replace with `tuple[X, ...]` |
| `Set[X]` | Replace with `set[X]` |
| `schema_extra` | Replace with `json_schema_extra` |
| `__fields__` | Replace with `model_fields` |
| `__validators__` | Replace with `__pydantic_validator__` |
