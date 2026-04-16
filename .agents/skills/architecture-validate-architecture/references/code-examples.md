# Architecture Validation Code Examples

## Validation Process Examples

### Step 1: Identify Architecture

```bash
# Read project documentation
Read ARCHITECTURE.md or README.md

# Identify pattern from keywords:
# - "Clean Architecture" → Clean
# - "Hexagonal" or "Ports and Adapters" → Hexagonal
# - "Layered" → Layered
# - "MVC" → MVC
```

### Step 2: Extract Layer Definitions

For Clean Architecture:
```
Domain Layer: domain/ (innermost)
Application Layer: application/
Infrastructure Layer: infrastructure/
Interface Layer: interfaces/ (outermost)
```

For Hexagonal:
```
Core/Domain: domain/
Ports: ports/ (interfaces)
Adapters: adapters/ (implementations)
```

### Step 3: Scan Imports

```bash
# Find all Python files
Glob: **/*.py (or **/*.js, **/*.ts for other languages)

# Extract imports from each file
Grep pattern: "^from .* import|^import "

# Categorize by layer based on file path
```

### Step 4: Validate Rules

**Clean Architecture Rules:**
```
Domain:
  ✅ Can import: domain only
  ❌ Cannot import: application, infrastructure, interfaces

Application:
  ✅ Can import: domain, application
  ❌ Cannot import: interfaces, infrastructure (concrete)

Infrastructure:
  ✅ Can import: domain, application (interfaces)
  ❌ Cannot import: interfaces (API/MCP layers)

Interface:
  ✅ Can import: application, domain
  ❌ Cannot import: infrastructure directly
```

### Step 5: Report Violations

```
❌ Architecture Validation: FAILED

Violations found:

1. [CRITICAL] Domain Layer Violation
   File: src/domain/models/entity.py:12
   Issue: Importing from infrastructure layer
   Code: from infrastructure.neo4j import Neo4jDriver
   Fix: Remove direct infrastructure dependency. Use repository interface instead.

2. [HIGH] Application Layer Violation
   File: src/application/services/search.py:8
   Issue: Importing from interfaces layer
   Code: from interfaces.mcp.tools import search_code
   Fix: Application should not know about interfaces. Move logic to application handler.

Total Violations: 2 (2 critical, 0 high, 0 medium)
```

## Architecture-Specific Detection Patterns

### Clean Architecture

**Dependency Rule**: Dependencies flow inward only

```
Interface → Application → Domain ← Infrastructure
   (UI)      (Use Cases)   (Core)    (External)
```

**Detection Patterns:**
```bash
# Domain violations
grep -rn "from.*\.\(application\|infrastructure\|interfaces\)" domain/

# Application violations
grep -rn "from.*\.interfaces" application/

# Interface violations
grep -rn "from.*\.infrastructure" interfaces/
```

### Hexagonal Architecture

**Dependency Rule**: Core has no dependencies, adapters depend on ports

```
   Adapters (Outside)
        ↓
   Ports (Interfaces)
        ↓
   Domain (Core)
```

**Detection Patterns:**
```bash
# Core violations
grep -rn "from.*\.\(adapters\|ports\)" domain/

# Adapter bypassing ports
grep -rn "from.*\.domain" adapters/ | grep -v "from.*\.ports"
```

### Layered Architecture

**Dependency Rule**: Each layer depends only on layer below

```
Presentation Layer
       ↓
Business Logic Layer
       ↓
Data Access Layer
```

**Detection Patterns:**
```bash
# Presentation bypassing business logic
grep -rn "from.*\.data" presentation/

# Data access depending on business
grep -rn "from.*\.business" data/
```

### MVC Architecture

**Dependency Rule**: Model is independent, View/Controller depend on Model

```
View → Controller → Model
  ↓         ↓
  ←─────────
```

**Detection Patterns:**
```bash
# Model violations
grep -rn "from.*\.\(views\|controllers\)" models/

# View importing Controller
grep -rn "from.*\.controllers" views/
```

## Common Anti-Patterns with Fixes

### 1. Domain Importing Infrastructure

```python
# ❌ VIOLATION
# domain/entities/user.py
from infrastructure.database import DatabaseConnection

# ✅ FIX
# domain/repositories/user_repository.py (interface)
class UserRepository(Protocol):
    def save(self, user: User) -> None: ...

# infrastructure/repositories/user_repository_impl.py
class UserRepositoryImpl:
    def __init__(self, db: DatabaseConnection):
        self.db = db
```

### 2. Application Importing Interfaces

```python
# ❌ VIOLATION
# application/services/search.py
from interfaces.api.routes import SearchEndpoint

# ✅ FIX
# application/handlers/search_handler.py
class SearchHandler:
    def handle(self, query: SearchQuery) -> SearchResult:
        # Application logic here
        pass

# interfaces/api/routes.py
@app.post("/search")
def search(query: str):
    handler = SearchHandler()
    return handler.handle(SearchQuery(query))
```

### 3. Circular Dependencies

```python
# ❌ VIOLATION
# service_a.py
from service_b import ServiceB

# service_b.py
from service_a import ServiceA

# ✅ FIX
# Extract shared interface/base class
# interfaces.py
class ServiceInterface(Protocol):
    def execute(self) -> Result: ...

# service_a.py
from interfaces import ServiceInterface

# service_b.py
from interfaces import ServiceInterface
```

### 4. Business Logic in Interface Layer

```python
# ❌ VIOLATION
# interfaces/api/routes.py
@app.post("/users")
def create_user(data: dict):
    # Validation, business rules, database save all here
    user = User(**data)
    if not user.email:
        raise ValueError("Email required")
    db.save(user)

# ✅ FIX
# application/commands/create_user.py
class CreateUserHandler:
    def handle(self, cmd: CreateUserCommand) -> ServiceResult[User]:
        # Business logic here
        pass

# interfaces/api/routes.py
@app.post("/users")
def create_user(data: dict):
    handler = CreateUserHandler()
    return handler.handle(CreateUserCommand(**data))
```

## Integration Examples

### With Pre-Commit Hooks

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python .claude/skills/validate-architecture/scripts/validate.py
if [ $? -ne 0 ]; then
    echo "❌ Architecture validation failed. Commit blocked."
    exit 1
fi
```

### With CI/CD Pipeline

Add to `.github/workflows/ci.yml`:
```yaml
- name: Validate Architecture
  run: python .claude/skills/validate-architecture/scripts/validate.py
```

### With Quality Gates

Add to `scripts/check_all.sh`:
```bash
echo "Validating architecture..."
python .claude/skills/validate-architecture/scripts/validate.py
```

## Customization Examples

### Define Custom Rules

Create `arch-rules.yaml` in project root:
```yaml
architecture: clean
layers:
  domain:
    path: src/core
    can_import: []
    cannot_import: [infrastructure, interfaces, application]

  application:
    path: src/usecases
    can_import: [domain]
    cannot_import: [interfaces]

severity:
  domain_violation: CRITICAL
  application_violation: HIGH
```

## Expected Output Examples

### Success (No Violations)

```
✅ Architecture Validation: PASSED

Pattern: Clean Architecture
Files checked: 127
Violations: 0

All layer boundaries respected.
Dependencies flow correctly (inward only).
No architectural anti-patterns detected.
```

### Failure (Violations Found)

```
❌ Architecture Validation: FAILED

Pattern: Clean Architecture
Files checked: 127
Violations: 5 (3 critical, 2 high, 0 medium)

Critical Violations:

1. Domain Layer Importing Infrastructure
   File: src/domain/models/entity.py:12
   Code: from infrastructure.neo4j import Neo4jDriver
   Fix: Use repository interface instead. Move Neo4jDriver to infrastructure layer.
   Impact: Breaks dependency inversion, couples domain to database

2. Application Layer Importing Interface
   File: src/application/services/search.py:8
   Code: from interfaces.mcp.tools import search_code
   Fix: Move business logic from interface to application handler
   Impact: Creates circular dependency risk

High Violations:

3. Circular Dependency Detected
   Files: service_a.py:5 ↔ service_b.py:8
   Fix: Extract shared interface or base class
   Impact: Difficult to test, fragile architecture

Summary:
- Fix critical violations before committing
- See Common Anti-Patterns Detected section above for detailed fix patterns
- Run validation again after fixes
```
