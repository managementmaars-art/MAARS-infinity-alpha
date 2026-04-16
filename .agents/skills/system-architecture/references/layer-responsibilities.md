# Layer Responsibilities Guide

Detailed guide on what belongs in each layer of the FastAPI + React/TypeScript architecture. Use this reference when deciding where to place new code.

---

## Backend Layers

### Routes (Routers)

**Location:** `app/routes/` or `app/api/`

**Responsibility:** HTTP interface — translate between HTTP and the application domain.

**DOES:**
- Parse and validate request data using Pydantic schemas
- Call service methods with validated data
- Return HTTP responses with appropriate status codes
- Handle HTTP-specific concerns (headers, cookies, content negotiation)
- Define FastAPI route decorators (`@router.get`, `@router.post`, etc.)
- Use `Depends()` for dependency injection (auth, services, pagination)
- Map domain exceptions to HTTP status codes via exception handlers

**DOES NOT:**
- Contain business logic or domain rules
- Access the database directly
- Import repository classes
- Transform data beyond HTTP serialization
- Make decisions about application behavior

**Example:**
```python
@router.post("/users", status_code=201, response_model=UserResponse)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    # Route only delegates to service — no logic here
    user = await service.create_user(data)
    return UserResponse.model_validate(user)
```

---

### Services

**Location:** `app/services/`

**Responsibility:** Business logic — the core of the application.

**DOES:**
- Implement business rules and domain logic
- Orchestrate operations across multiple repositories
- Validate business constraints (e.g., "user must have verified email to post")
- Raise domain-specific exceptions (`NotFoundError`, `ConflictError`)
- Coordinate transactions when multiple writes are needed
- Emit domain events (if using event-driven patterns)
- Apply authorization rules ("can this user perform this action?")

**DOES NOT:**
- Know about HTTP (no `Request`, `Response`, `HTTPException`, status codes)
- Execute raw SQL queries
- Import route modules
- Handle serialization to/from JSON
- Manage database sessions directly (receive via injection)

**Example:**
```python
class UserService:
    def __init__(self, repo: UserRepository, email_service: EmailService) -> None:
        self.repo = repo
        self.email_service = email_service

    async def create_user(self, data: UserCreate) -> User:
        # Business rule: check for duplicate email
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictError(f"Email {data.email} already registered")

        # Business logic: hash password, create user
        hashed = hash_password(data.password)
        user = await self.repo.create(email=data.email, hashed_password=hashed)

        # Side effect: send welcome email
        await self.email_service.send_welcome(user.email)

        return user
```

---

### Repositories

**Location:** `app/repositories/`

**Responsibility:** Data access — encapsulate all database interactions.

**DOES:**
- Execute database queries (SELECT, INSERT, UPDATE, DELETE)
- Use SQLAlchemy ORM or Core for query construction
- Handle query optimization (eager loading, pagination, filtering)
- Return model instances, lists, or None
- Apply database-level constraints (unique checks via queries)
- Manage query-level concerns (ordering, limiting, offsetting)

**DOES NOT:**
- Contain business logic or validation rules
- Raise domain exceptions (raise data-layer exceptions or return None)
- Know about HTTP or API contracts
- Import service classes
- Handle transactions (the service or middleware manages transaction scope)
- Transform data into response formats

**Example:**
```python
class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()  # Get the ID without committing
        return user
```

---

### Models

**Location:** `app/models/`

**Responsibility:** Database schema definition — map Python classes to database tables.

**DOES:**
- Define table columns with types, constraints, and defaults
- Define relationships between tables (foreign keys, back_populates)
- Define indexes (single-column, composite, partial)
- Use SQLAlchemy 2.0 `Mapped` type annotations
- Specify eager loading strategy on relationships (`lazy="selectin"` for async)

**DOES NOT:**
- Contain business logic or methods
- Import services or repositories
- Define API-facing schemas (that's Pydantic's job)
- Manage sessions or transactions

**Conventions:**
- Table names: plural snake_case (`users`, `blog_posts`)
- Column names: snake_case (`created_at`, `is_active`)
- Always set `lazy="selectin"` or `lazy="joined"` for async compatibility
- Use `server_default` for database-level defaults (e.g., `func.now()`)
- Define `__repr__` for debugging convenience

---

### Schemas (Pydantic v2)

**Location:** `app/schemas/`

**Responsibility:** Data validation and serialization — define the shape of data at API boundaries.

**DOES:**
- Validate request data (types, constraints, formats)
- Define response shapes (what fields are exposed to the client)
- Apply field-level validation (min/max length, regex, email format)
- Apply model-level validation (cross-field constraints)
- Provide serialization/deserialization between JSON and Python objects

**DOES NOT:**
- Contain business logic
- Access the database
- Import models directly (use `model_validate()` for ORM → schema conversion)

**Naming conventions:**
- `{Resource}Create` — POST request body (e.g., `UserCreate`)
- `{Resource}Update` — PUT/PATCH request body (e.g., `UserUpdate`)
- `{Resource}Response` — Response body (e.g., `UserResponse`)
- `{Resource}Filter` — Query parameters for filtering (e.g., `UserFilter`)
- `{Resource}ListResponse` — Paginated list response (e.g., `UserListResponse`)

---

## Frontend Layers

### Pages

**Location:** `src/pages/`

**Responsibility:** Route-level components — compose features and layouts for a URL.

**DOES:**
- Fetch data needed for the page (via TanStack Query hooks)
- Compose layout and feature components
- Handle page-level loading and error states
- Define page metadata (title, description)

**DOES NOT:**
- Contain reusable UI components
- Define data fetching logic (that lives in hooks)
- Implement complex business logic

---

### Features

**Location:** `src/features/`

**Responsibility:** Domain-specific UI — composed from shared components and hooks.

**DOES:**
- Implement domain-specific UI (UserProfile, OrderList, ChatPanel)
- Use custom hooks for data and state management
- Compose shared components with domain-specific props
- Handle feature-specific interactions and state

**DOES NOT:**
- Make direct API calls (use hooks)
- Define reusable generic components (those go in `components/`)

---

### Shared Components

**Location:** `src/components/`

**Responsibility:** Reusable UI primitives — generic, configurable via props.

**DOES:**
- Render UI elements (Button, Modal, Table, Form, Input, Card)
- Accept configuration via props (variant, size, disabled, onClick)
- Handle visual states (hover, focus, loading, disabled)
- Implement accessibility (ARIA attributes, keyboard navigation)

**DOES NOT:**
- Fetch data or manage server state
- Contain business logic
- Import feature-level components

---

### Hooks

**Location:** `src/hooks/`

**Responsibility:** Reusable stateful logic — abstract away complexity from components.

**DOES:**
- Wrap TanStack Query calls (useQuery, useMutation)
- Manage complex local state (useReducer patterns)
- Encapsulate browser API interactions (useMediaQuery, useLocalStorage)
- Provide domain-specific logic (useAuth, usePagination, useDebounce)

**Naming:** Always prefix with `use` (e.g., `useAuth`, `useUsers`, `useDebounce`)

---

### API Layer

**Location:** `src/api/`

**Responsibility:** API client — define how to communicate with the backend.

**DOES:**
- Define API endpoint functions (e.g., `fetchUsers`, `createUser`)
- Configure HTTP client (axios/fetch with base URL, interceptors)
- Define TanStack Query options using `queryOptions()` factory
- Handle token injection and refresh

**DOES NOT:**
- Manage UI state
- Handle errors (let TanStack Query and components handle display)

---

## Decision Guide: Where Does This Code Go?

| If the code... | Put it in... |
|----------------|-------------|
| Parses HTTP request or formats HTTP response | Routes |
| Enforces a business rule | Services |
| Queries or writes to the database | Repositories |
| Defines a table schema | Models |
| Validates input or shapes output | Schemas |
| Composes UI for a URL | Pages |
| Implements domain-specific UI | Features |
| Is a reusable UI element | Shared Components |
| Manages stateful logic for components | Hooks |
| Calls the backend API | API Layer |
