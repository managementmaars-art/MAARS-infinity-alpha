# Project Patterns - your_project Specific SRP Patterns

## Overview

This reference documents your_project's architectural patterns and how they enforce Single Responsibility Principle through Clean Architecture layers. Each layer has specific actor constraints that prevent SRP violations.

---

## Clean Architecture Layer Rules

### Domain Layer (actor: business rules)

**Responsibility**: Pure business logic and domain models, no external dependencies.

**Allowed**:
- Entity classes with business rules
- Value objects (immutable data)
- Domain services (pure logic)
- Repository protocols (interfaces only)
- Business rule validation

**Forbidden**:
- I/O operations (database, file system, network)
- Framework dependencies
- Infrastructure concerns
- Application workflow logic
- External service calls

**SRP Rule**: Domain entities serve ONE business rules actor only.

**✅ GOOD Examples**:

```python
# File: src/domain/models/files/file.py
class File:
    """Domain entity representing a source code file."""

    def __init__(
        self,
        identity: Identity,
        location: Location,
        file_type: FileType,
        language: Language | None,
        content_hash: ContentHash,
        events: Events | None = None
    ):
        # Actor: Business rules (file representation)
        # Pure domain logic, no I/O
        self._identity = identity
        self._location = location
        self._file_type = file_type
        self._language = language
        self._content_hash = content_hash
        self._events = events or Events()

    @property
    def is_indexable(self) -> bool:
        """Business rule: which files should be indexed."""
        return self._file_type.is_code_file()
```

```python
# File: src/domain/values/content_hash.py
@dataclass(frozen=True)
class ContentHash:
    """Value object for file content hash."""

    value: str

    def __post_init__(self):
        # Actor: Business rules (hash validation)
        if not self.value or len(self.value) != 64:
            raise ValueError(f"Invalid content hash: {self.value}")

    def matches(self, other: "ContentHash") -> bool:
        """Business rule: hash equality."""
        return self.value == other.value
```

**❌ BAD Examples**:

```python
# ❌ VIOLATION: Domain entity doing I/O
class File:
    def save(self):
        # WRONG: Database operation in domain layer
        # Serves two actors: business rules + persistence
        db.execute("INSERT INTO files ...")

    def load_content(self) -> str:
        # WRONG: File I/O in domain layer
        # Serves two actors: business rules + file system
        with open(self.path) as f:
            return f.read()
```

```python
# ❌ VIOLATION: Domain entity with application logic
class User:
    def create_and_notify(self):
        # WRONG: Orchestration in domain layer
        # Serves three actors: business rules + persistence + notification
        self.validate()
        self.save()
        self.send_welcome_email()
```

---

### Application Layer (actor: use case coordinator)

**Responsibility**: Orchestrate use cases, coordinate domain and infrastructure.

**Allowed**:
- Command/query handlers (one per use case)
- Orchestrators (workflow coordination)
- Application services (use case execution)
- DTO transformations
- Cross-cutting concerns (logging, metrics)

**Forbidden**:
- Business logic (belongs in domain)
- Direct database queries (use repositories)
- Infrastructure implementation details
- Multiple use cases in one handler

**SRP Rule**: One handler/orchestrator serves ONE use case actor only.

**✅ GOOD Examples**:

```python
# File: src/application/orchestration/indexing_orchestrator.py
class IndexingOrchestrator:
    """
    Orchestrates the three-phase indexing workflow.

    Actor: Indexing workflow coordinator
    Responsibility: Phase sequencing, metrics aggregation, error handling
    """

    def __init__(
        self,
        settings: Settings,
        indexing_module: IndexingModule,
        extractor_registry: ExtractorRegistry,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
    ):
        # Required dependencies injected, no defaults
        if not settings:
            raise ValueError("settings required")
        # ... validate all dependencies

        self._settings = settings
        self._indexing_module = indexing_module
        self._extractor_registry = extractor_registry
        self._chunking_service = chunking_service
        self._embedding_service = embedding_service

    async def index_files(self, files: list[File]) -> ServiceResult[IndexingMetrics]:
        """
        Single responsibility: coordinate indexing workflow.

        Does NOT:
        - Contain business logic (delegates to domain)
        - Execute database queries (delegates to infrastructure)
        - Implement extraction logic (delegates to services)
        """
        # Phase 1: Extract entities
        extraction_result = await self._extract_entities(files)
        if not extraction_result.success:
            return extraction_result

        # Phase 2: Create relationships
        relationship_result = await self._create_relationships(files)
        if not relationship_result.success:
            return relationship_result

        # Phase 3: Resolve cross-file relationships
        resolution_result = await self._resolve_relationships()

        return ServiceResult.success(self._aggregate_metrics())
```

```python
# File: src/application/commands/refresh_repository.py
class RefreshRepositoryHandler:
    """
    Handle RefreshRepository command.

    Actor: Repository refresh use case
    Responsibility: Single use case execution only
    """

    def __init__(
        self,
        indexing_orchestrator: IndexingOrchestrator,
        file_scanner: FileScanner,
        settings: Settings
    ):
        # One handler = one use case
        if not indexing_orchestrator:
            raise ValueError("indexing_orchestrator required")
        if not file_scanner:
            raise ValueError("file_scanner required")
        if not settings:
            raise ValueError("settings required")

        self._orchestrator = indexing_orchestrator
        self._scanner = file_scanner
        self._settings = settings

    async def handle(
        self,
        command: RefreshRepositoryCommand
    ) -> ServiceResult[RefreshResult]:
        """Execute single use case: refresh repository."""
        # Just orchestration, no business logic
        files = await self._scanner.scan(command.path)
        result = await self._orchestrator.index_files(files)
        return ServiceResult.success(RefreshResult(files=len(files)))
```

**❌ BAD Examples**:

```python
# ❌ VIOLATION: Multiple use cases in one handler
class UserHandler:
    def create_user(self, data): pass   # Use case 1
    def update_user(self, data): pass   # Use case 2
    def delete_user(self, id): pass     # Use case 3
    def list_users(self): pass          # Use case 4
    # Serves four different actors (create workflow, update workflow, etc.)
```

```python
# ❌ VIOLATION: Business logic in application layer
class UserService:
    def create_user(self, data: dict) -> ServiceResult[User]:
        # WRONG: Business rule in application layer
        if data["age"] < 18:  # Business logic here!
            return ServiceResult.failure("Must be adult")

        # Business logic belongs in domain
        user = User(data["name"], data["age"])
        return self.repository.save(user)
```

```python
# ❌ VIOLATION: Optional config parameters
class IndexingOrchestrator:
    def __init__(
        self,
        settings: Settings | None = None,  # WRONG!
        indexing_module: IndexingModule | None = None  # WRONG!
    ):
        # Creates two actors: configured mode + default mode
        self.settings = settings or Settings()
        self.indexing_module = indexing_module or IndexingModule()
```

---

### Infrastructure Layer (actor: external system integrator)

**Responsibility**: Implement domain interfaces for external systems.

**Allowed**:
- Repository implementations
- External service adapters
- Database queries
- File system operations
- Network calls
- Framework-specific code

**Forbidden**:
- Business logic (belongs in domain)
- Use case orchestration (belongs in application)
- Multiple external systems in one class

**SRP Rule**: One repository serves ONE external system actor only.

**✅ GOOD Examples**:

```python
# File: src/infrastructure/neo4j/code_repository.py
class Neo4jCodeRepository(CodeRepository, ManagedResource):
    """
    Neo4j adapter implementing the CodeRepository interface.

    Actor: Neo4j database system
    Responsibility: Code storage operations using Neo4j only
    """

    def __init__(
        self,
        driver: AsyncDriver,
        settings: Settings,
        index_manager: IndexManager,
    ):
        # Required dependencies, no defaults
        if not driver:
            raise ValueError("Neo4j driver is required")
        if not settings:
            raise ValueError("Settings is required")
        if not index_manager:
            raise ValueError("IndexManager is required")

        self.driver = driver
        self.settings = settings
        self.database = settings.neo4j.database_name
        self._index_manager = index_manager

    async def save_file(self, file: File) -> ServiceResult[None]:
        """Single responsibility: persist file to Neo4j."""
        query = CypherQueries.CREATE_FILE
        params = self._file_to_params(file)
        return await self._execute_with_retry(query, params)

    async def find_by_id(self, file_id: str) -> ServiceResult[File | None]:
        """Single responsibility: retrieve file from Neo4j."""
        query = CypherQueries.FIND_FILE_BY_ID
        result = await self._execute_with_retry(query, {"id": file_id})

        if not result.success or not result.value:
            return ServiceResult.success(None)

        return ServiceResult.success(self._record_to_file(result.value[0]))
```

**❌ BAD Examples**:

```python
# ❌ VIOLATION: Multiple external systems
class UserRepository:
    def save_to_neo4j(self, user): pass        # System 1: Neo4j
    def cache_in_redis(self, user): pass       # System 2: Redis
    def index_in_elasticsearch(self, user): pass  # System 3: Elasticsearch
    # Serves three different actors (Neo4j team, Redis team, ES team)
```

```python
# ❌ VIOLATION: Repository with orchestration
class CodeRepository:
    def save_and_index(self, file: File):
        # WRONG: Orchestration in infrastructure layer
        self.save_file(file)
        self.create_embeddings(file)
        self.update_search_index(file)
        # Serves three actors: persistence + embedding + search
```

---

### Interface Layer (actor: external consumer)

**Responsibility**: Expose application to external consumers (MCP, CLI, API).

**Allowed**:
- Tool registrars (MCP tools)
- API endpoints
- CLI commands
- Request/response DTOs
- Input validation
- Intentional facades

**Forbidden**:
- Business logic (belongs in domain)
- Direct database access (use repositories)
- Application workflow (use handlers/orchestrators)

**SRP Rule**: One tool/endpoint serves ONE external operation actor only.

**✅ GOOD Examples**:

```python
# File: src/interfaces/mcp/tool_registrars/search_tools.py
class SearchToolRegistrar(BaseToolRegistrar):
    """
    Register MCP tools for code search operations.

    Actor: MCP tool consumer
    Responsibility: Expose search operations to MCP clients
    """

    def __init__(
        self,
        container: Container,
        mcp: FastMCP,
        settings: Settings
    ):
        if not container:
            raise ValueError("container required")
        if not mcp:
            raise ValueError("mcp required")
        if not settings:
            raise ValueError("settings required")

        super().__init__(container, mcp, settings)

    def register_tools(self) -> None:
        """Register all search-related MCP tools."""

        @self._mcp.tool()
        async def search_code(
            query: str,
            search_type: Literal["semantic", "hybrid"] = "semantic"
        ) -> str:
            """Search indexed code using semantic or hybrid search."""
            # Single responsibility: expose search operation
            handler = self._container.get_search_handler()
            command = SearchCommand(query=query, type=search_type)
            result = await handler.handle(command)

            # Convert ServiceResult to MCP response
            return self._format_response(result)
```

**❌ BAD Examples**:

```python
# ❌ VIOLATION: Tool with business logic
@mcp.tool()
async def create_user(name: str, age: int) -> str:
    # WRONG: Business logic in interface layer
    if age < 18:  # Business rule here!
        return "Error: Must be adult"

    # Business logic belongs in domain
    user = User(name, age)
    await repository.save(user)
    return "User created"
```

---

## Project-Specific Anti-Patterns

### 1. Optional Config Parameters

**Rule**: Never use `Type | None = None` for required dependencies.

**Why**: Creates two actors (configured mode + default mode), violates fail-fast principle.

**❌ WRONG**:

```python
class UserService:
    def __init__(
        self,
        settings: Settings | None = None,  # Anti-pattern!
        logger: Logger | None = None
    ):
        # Creates multiple code paths = multiple actors
        self.settings = settings or Settings()  # Default creation
        self.logger = logger or get_logger(__name__)
```

**✅ CORRECT**:

```python
class UserService:
    def __init__(self, settings: Settings, logger: Logger):
        # Required dependencies, fail fast
        if not settings:
            raise ValueError("settings required")
        if not logger:
            raise ValueError("logger required")

        self.settings = settings
        self.logger = logger
```

**Detection**:

```yaml
id: optional-config-anti-pattern
language: python
rule:
  pattern: "$NAME: $TYPE | None = None"
  inside:
    kind: function_definition
    pattern: "def __init__"
```

**Confidence**: 90% (critical violation)

---

### 2. Try/Except ImportError

**Rule**: All imports at module top level, no conditional imports.

**Why**: Creates multiple code paths (dependency available + fallback), violates fail-fast.

**❌ WRONG**:

```python
try:
    from radon.complexity import cc_visit
    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False

class ComplexityAnalyzer:
    def analyze(self, code: str):
        if RADON_AVAILABLE:  # Multiple actors!
            return cc_visit(code)
        else:
            return self._fallback_analysis(code)
```

**✅ CORRECT**:

```python
# Fail fast at import time
from radon.complexity import cc_visit  # If missing, fail immediately

class ComplexityAnalyzer:
    def analyze(self, code: str):
        # Single code path, single actor
        return cc_visit(code)
```

**Detection**: Use `validate-fail-fast-imports` skill.

**Confidence**: 90% (critical violation)

---

### 3. Bare None Returns

**Rule**: All service methods return `ServiceResult[T]`, never bare `None` on error.

**Why**: Creates two return paths (success value + None), violates error handling actor.

**❌ WRONG**:

```python
async def find_user(self, user_id: str) -> User | None:
    # WRONG: Bare None for errors
    try:
        result = await self.db.query(...)
        return User.from_dict(result)
    except Exception:
        return None  # What went wrong? Unknown!
```

**✅ CORRECT**:

```python
async def find_user(self, user_id: str) -> ServiceResult[User | None]:
    # Single actor: result monad
    try:
        result = await self.db.query(...)
        if not result:
            return ServiceResult.success(None)  # Not found (success)
        return ServiceResult.success(User.from_dict(result))
    except Exception as e:
        return ServiceResult.failure(str(e))  # Error with context
```

**Detection**: Type checking with pyright.

**Confidence**: 80% (critical violation)

---

### 4. Methods with "and" in Name

**Rule**: Method names should describe single action, not multiple steps.

**Why**: Name indicates serving multiple actors.

**❌ WRONG**:

```python
def validate_and_save_user(self, user: User):
    # Serves two actors: validation rules + persistence
    self.validate(user)
    self.save(user)

def fetch_and_process_data(self, data_id: str):
    # Serves two actors: data retrieval + processing logic
    data = self.fetch(data_id)
    return self.process(data)
```

**✅ CORRECT**:

```python
# Split by actor
def validate_user(self, user: User) -> ServiceResult[User]:
    # Actor: validation rules
    pass

def save_user(self, user: User) -> ServiceResult[None]:
    # Actor: persistence
    pass

# Or use orchestrator
def create_user_workflow(self, user: User) -> ServiceResult[User]:
    # Actor: workflow coordinator
    validated = self.validate_user(user)
    if not validated.success:
        return validated
    return self.save_user(validated.value)
```

**Detection**:

```yaml
id: method-name-and
language: python
rule:
  pattern: "def $NAME_and_$REST"
```

**Confidence**: 40% (review needed)

---

## CQRS Pattern

**Rule**: One handler per command/query, never multiple use cases in one handler.

**Why**: Each use case is a separate actor.

**✅ GOOD Examples**:

```python
# File: src/application/commands/create_user.py
class CreateUserHandler:
    """Handle CreateUser command only."""

    def handle(self, command: CreateUserCommand) -> ServiceResult[User]:
        # Single use case
        pass

# File: src/application/commands/update_user.py
class UpdateUserHandler:
    """Handle UpdateUser command only."""

    def handle(self, command: UpdateUserCommand) -> ServiceResult[User]:
        # Different use case, different handler
        pass

# File: src/application/queries/find_user.py
class FindUserHandler:
    """Handle FindUser query only."""

    def handle(self, query: FindUserQuery) -> ServiceResult[User | None]:
        # Query use case
        pass
```

**❌ BAD Examples**:

```python
# ❌ VIOLATION: Multiple use cases in one handler
class UserHandler:
    def create(self, cmd: CreateUserCommand): pass   # Use case 1
    def update(self, cmd: UpdateUserCommand): pass   # Use case 2
    def delete(self, cmd: DeleteUserCommand): pass   # Use case 3
    def find(self, query: FindUserQuery): pass       # Use case 4
    # Serves four different actors!
```

---

## Repository Pattern

**Rule**: Protocol in domain, implementation in infrastructure. One repository per entity or aggregate.

**✅ GOOD Examples**:

```python
# File: src/domain/repositories/code_repository.py
class CodeRepository(Protocol):
    """Protocol defining code storage operations."""

    async def save_file(self, file: File) -> ServiceResult[None]:
        """Save a file to storage."""
        ...

    async def find_by_id(self, file_id: str) -> ServiceResult[File | None]:
        """Find file by ID."""
        ...

# File: src/infrastructure/neo4j/code_repository.py
class Neo4jCodeRepository(CodeRepository, ManagedResource):
    """Neo4j implementation of CodeRepository."""

    async def save_file(self, file: File) -> ServiceResult[None]:
        # Implementation for Neo4j
        pass

    async def find_by_id(self, file_id: str) -> ServiceResult[File | None]:
        # Implementation for Neo4j
        pass
```

**❌ BAD Examples**:

```python
# ❌ VIOLATION: Repository for multiple aggregates
class Repository:
    # Multiple aggregates = multiple actors
    async def save_user(self, user): pass
    async def save_product(self, product): pass
    async def save_order(self, order): pass
```

---

## When to Allow "Violations"

### 1. Intentional Facades

Facades aggregate multiple services for simplified external API.

**✅ ALLOWED**:

```python
class UserServiceFacade:
    """
    Simplified interface for external consumers.

    Actor: External API consumer
    Responsibility: Provide simplified interface (intentional aggregation)
    """

    def __init__(
        self,
        validator: UserValidator,
        repository: UserRepository,
        notifier: UserNotifier
    ):
        self._validator = validator
        self._repository = repository
        self._notifier = notifier

    def create_user(self, data: dict) -> ServiceResult[User]:
        """Single actor: external consumer convenience."""
        validated = self._validator.validate(data)
        if not validated.success:
            return validated

        saved = self._repository.save(validated.value)
        if not saved.success:
            return saved

        # Fire-and-forget notification
        self._notifier.notify(saved.value)

        return saved
```

**When**: Interface layer for external consumers, clearly documented as facade.

---

### 2. Value Objects with Helpers

Value objects can have multiple helper methods serving same actor.

**✅ ALLOWED**:

```python
@dataclass(frozen=True)
class ContentHash:
    """
    Value object for file content hash.

    Actor: Hash representation and comparison
    """

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) != 64:
            raise ValueError("Invalid hash")

    def matches(self, other: "ContentHash") -> bool:
        return self.value == other.value

    def to_short_form(self) -> str:
        return self.value[:8]

    def to_dict(self) -> dict:
        return {"hash": self.value}

    @classmethod
    def from_content(cls, content: str) -> "ContentHash":
        import hashlib
        return cls(hashlib.sha256(content.encode()).hexdigest())
```

**When**: All methods serve same actor (value representation).

---

### 3. Cohesive Private Methods

Private helper methods supporting single public interface.

**✅ ALLOWED**:

```python
class UserValidator:
    """
    Actor: User validation rules
    """

    def validate(self, user: User) -> ServiceResult[User]:
        """Single public interface."""
        self._check_name(user.name)
        self._check_email(user.email)
        self._check_age(user.age)
        return ServiceResult.success(user)

    def _check_name(self, name: str) -> None:
        # Private helper for validation actor
        pass

    def _check_email(self, email: str) -> None:
        # Private helper for validation actor
        pass

    def _check_age(self, age: int) -> None:
        # Private helper for validation actor
        pass
```

**When**: Private methods support single responsibility, not exposed externally.

---

## Summary

### Layer-Specific SRP Rules

| Layer | Actor Type | Allowed | Forbidden |
|-------|-----------|---------|-----------|
| **Domain** | Business rules | Entities, value objects, protocols | I/O, frameworks, orchestration |
| **Application** | Use case | Handlers (1 per use case), orchestrators | Business logic, direct DB, multiple use cases |
| **Infrastructure** | External system | Repository impls (1 per system) | Business logic, orchestration, multiple systems |
| **Interface** | External consumer | Tools (1 per operation), facades | Business logic, direct DB, workflows |

### Anti-Pattern Detection

| Anti-Pattern | Confidence | Fix |
|--------------|-----------|-----|
| Optional config (`Type \| None = None`) | 90% | Required injection with validation |
| Try/except ImportError | 90% | Fail-fast imports at top |
| Bare None returns | 80% | ServiceResult monad |
| Methods with "and" | 40% | Split by actor |
| Multiple use cases in handler | 80% | One handler per use case |
| Domain entity I/O | 90% | Move to infrastructure |

### Integration

- Use with `validate-architecture` skill for layer boundary enforcement
- Use with `code-review` skill for pre-commit SRP validation
- Use with `run-quality-gates` for automated quality checks
- Use with `multi-file-refactor` skill for SRP refactoring across files
