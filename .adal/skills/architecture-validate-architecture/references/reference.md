# Architecture Validation Reference

## Complete Layer Dependency Matrices

### Clean Architecture

#### Layer Structure
```
┌─────────────────────────────────────┐
│      Interface Layer (Outermost)    │  Entry points: API, CLI, MCP
│  ┌───────────────────────────────┐  │
│  │   Infrastructure Layer        │  │  External services: DB, APIs
│  │  ┌─────────────────────────┐  │  │
│  │  │  Application Layer      │  │  │  Use cases, orchestration
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │  Domain Layer     │  │  │  │  Pure business logic
│  │  │  │  (Core)           │  │  │  │
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘

Dependencies flow INWARD ONLY (→)
```

#### Dependency Rules Matrix

| From Layer      | To Domain | To Application | To Infrastructure | To Interface |
|----------------|-----------|----------------|-------------------|--------------|
| Domain         | ✅ Yes     | ❌ No          | ❌ No             | ❌ No        |
| Application    | ✅ Yes     | ✅ Yes         | ❌ No (concrete)  | ❌ No        |
| Infrastructure | ✅ Yes     | ✅ Yes (interfaces) | ✅ Yes      | ❌ No        |
| Interface      | ✅ Yes     | ✅ Yes         | ❌ No             | ✅ Yes       |

#### Detailed Rules

**Domain Layer** (`domain/`)
- **Can import**:
  - Other domain modules
  - Standard library only
  - Type hints from `typing`
- **Cannot import**:
  - Application layer
  - Infrastructure layer
  - Interface layer
  - External frameworks (Django, Flask, FastAPI, etc.)
  - Database libraries (SQLAlchemy, Neo4j driver, etc.)
- **Contains**:
  - Entity definitions
  - Value objects
  - Domain events
  - Repository interfaces (ports)
  - Business rules and validation
- **Examples**:
  ```python
  # ✅ ALLOWED
  from domain.entities import User
  from domain.values import EmailAddress
  from typing import Protocol, Optional

  # ❌ FORBIDDEN
  from application.services import UserService
  from infrastructure.database import Database
  from interfaces.api import UserEndpoint
  from sqlalchemy import Column, Integer
  ```

**Application Layer** (`application/`)
- **Can import**:
  - Domain layer (entities, value objects, ports)
  - Other application modules
  - Standard library
- **Cannot import**:
  - Interface layer (API, CLI, MCP)
  - Concrete infrastructure implementations
- **Can define**:
  - Interfaces that infrastructure will implement
  - DTOs for cross-layer communication
- **Contains**:
  - Use case handlers (commands/queries)
  - Application services
  - DTOs
  - Orchestration logic
- **Examples**:
  ```python
  # ✅ ALLOWED
  from domain.entities import User
  from domain.repositories import UserRepository  # Port/Interface
  from application.dto import UserDTO

  # ❌ FORBIDDEN
  from interfaces.api.routes import user_routes
  from infrastructure.neo4j.user_repo import Neo4jUserRepo  # Concrete impl
  ```

**Infrastructure Layer** (`infrastructure/`)
- **Can import**:
  - Domain layer (to implement interfaces)
  - Application layer (interfaces only)
  - External libraries and frameworks
  - Other infrastructure modules
- **Cannot import**:
  - Interface layer (API, CLI, MCP)
- **Contains**:
  - Repository implementations
  - Database adapters
  - External API clients
  - File system operations
  - Cache implementations
- **Examples**:
  ```python
  # ✅ ALLOWED
  from domain.repositories import UserRepository
  from domain.entities import User
  from neo4j import AsyncDriver
  from application.interfaces import SearchService  # Application-defined interface

  # ❌ FORBIDDEN
  from interfaces.api import app
  from interfaces.mcp.tools import search_code
  ```

**Interface Layer** (`interfaces/`)
- **Can import**:
  - Application layer (handlers, DTOs)
  - Domain layer (for type hints, not business logic)
  - Other interface modules
  - Framework-specific code (FastAPI, Click, etc.)
- **Cannot import**:
  - Infrastructure layer implementations directly
- **Must**:
  - Delegate all business logic to application layer
  - Transform external formats to application DTOs
- **Contains**:
  - API endpoints/routes
  - CLI commands
  - MCP tool definitions
  - Request/response models (not business logic)
- **Examples**:
  ```python
  # ✅ ALLOWED
  from application.handlers import CreateUserHandler
  from application.dto import CreateUserDTO
  from domain.entities import User  # For type hints only
  from fastapi import FastAPI

  # ❌ FORBIDDEN
  from infrastructure.database import Neo4jConnection
  from infrastructure.repositories import UserRepositoryImpl

  # ❌ FORBIDDEN - Business logic in interface
  @app.post("/users")
  def create_user(data: dict):
      # Business validation, database save - WRONG!
      user = User(**data)
      db.save(user)

  # ✅ CORRECT - Delegate to application
  @app.post("/users")
  def create_user(data: dict):
      handler = CreateUserHandler()
      result = handler.handle(CreateUserDTO(**data))
      return result
  ```

### Hexagonal Architecture (Ports and Adapters)

#### Layer Structure
```
┌───────────────────────────────────────┐
│         Adapters (Outside)            │
│  ┌─────────────────────────────────┐  │
│  │      Ports (Interfaces)         │  │
│  │  ┌───────────────────────────┐  │  │
│  │  │   Domain/Core (Inside)    │  │  │
│  │  └───────────────────────────┘  │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘

Adapters depend on Ports
Ports defined by Core
Core has NO dependencies
```

#### Dependency Rules Matrix

| From Layer | To Core | To Ports | To Adapters |
|-----------|---------|----------|-------------|
| Core      | ✅ Yes   | ❌ No    | ❌ No       |
| Ports     | ✅ Yes   | ✅ Yes   | ❌ No       |
| Adapters  | ❌ No    | ✅ Yes   | ✅ Yes      |

#### Detailed Rules

**Core/Domain** (`domain/` or `core/`)
- **Can import**: Core modules only, standard library
- **Cannot import**: Ports, Adapters, external frameworks
- **Contains**: Pure business logic, domain entities, domain events

**Ports** (`ports/` or defined in core)
- **Can import**: Core/Domain
- **Cannot import**: Adapters
- **Contains**: Interfaces (protocols) for input/output

**Adapters** (`adapters/` or split into `primary/` and `secondary/`)
- **Can import**: Ports only
- **Cannot import**: Core directly (use ports)
- **Contains**:
  - Primary (driving): API, CLI, web UI
  - Secondary (driven): Database, external APIs, file system

### Layered Architecture

#### Layer Structure
```
┌─────────────────────────────┐
│   Presentation Layer        │  UI, API endpoints
├─────────────────────────────┤
│   Business Logic Layer      │  Services, validation
├─────────────────────────────┤
│   Data Access Layer         │  Repositories, DB
└─────────────────────────────┘

Each layer depends ONLY on layer below
```

#### Dependency Rules Matrix

| From Layer     | To Presentation | To Business | To Data |
|---------------|-----------------|-------------|---------|
| Presentation  | ✅ Yes           | ✅ Yes      | ❌ No   |
| Business      | ❌ No            | ✅ Yes      | ✅ Yes  |
| Data          | ❌ No            | ❌ No       | ✅ Yes  |

#### Detailed Rules

**Presentation Layer** (`presentation/` or `ui/`)
- **Can import**: Business logic layer
- **Cannot import**: Data access layer directly
- **Contains**: Controllers, views, API routes, request handlers

**Business Logic Layer** (`business/` or `services/`)
- **Can import**: Data access layer
- **Cannot import**: Presentation layer
- **Contains**: Business rules, validation, orchestration

**Data Access Layer** (`data/` or `repositories/`)
- **Can import**: Data layer modules only
- **Cannot import**: Business or presentation layers
- **Contains**: Repositories, database connections, ORM models

### MVC Architecture

#### Layer Structure
```
     ┌──────────┐
     │   View   │
     └────┬─────┘
          │
     ┌────▼────────┐
     │ Controller  │
     └────┬────────┘
          │
     ┌────▼─────┐
     │  Model   │
     └──────────┘

Model is independent
View/Controller depend on Model
View observes Model
```

#### Dependency Rules Matrix

| From Layer | To Model | To View | To Controller |
|-----------|----------|---------|---------------|
| Model     | ✅ Yes    | ❌ No   | ❌ No         |
| View      | ✅ Yes    | ✅ Yes  | ❌ No         |
| Controller| ✅ Yes    | ✅ Yes  | ✅ Yes        |

#### Detailed Rules

**Model** (`models/`)
- **Can import**: Other models, standard library
- **Cannot import**: Views, Controllers
- **Contains**: Business entities, validation, business rules

**View** (`views/` or `templates/`)
- **Can import**: Models (for display)
- **Cannot import**: Controllers
- **Contains**: UI logic, templates, presentation

**Controller** (`controllers/`)
- **Can import**: Models, Views
- **Cannot import**: Nothing (top-level orchestrator)
- **Contains**: Request handling, coordination between Model and View

## Detection Patterns by Language

### Python

**Import Statement Patterns:**
```python
# Absolute imports
from package.module import Class
import package.module

# Relative imports (should detect layer violations)
from ..infrastructure import Database
from ...domain import Entity
```

**Grep Patterns:**
```bash
# Find all imports
grep -rn "^from .* import\|^import " src/

# Find domain importing from outer layers
grep -rn "from.*\.\(application\|infrastructure\|interfaces\)" domain/

# Find application importing interfaces
grep -rn "from.*\.interfaces" application/

# Find circular imports
grep -rn "from service_a import" service_b.py
grep -rn "from service_b import" service_a.py
```

### JavaScript/TypeScript

**Import Statement Patterns:**
```javascript
// ES6 imports
import { Class } from './module';
import * as Module from './module';

// CommonJS
const Module = require('./module');
```

**Grep Patterns:**
```bash
# Find all imports
grep -rn "^import .* from\|^const .* = require" src/

# Find domain importing from outer layers
grep -rn "import.*from.*\.\./\.\./\(infrastructure\|interfaces\)" domain/
```

## Severity Levels

### CRITICAL
- Domain layer importing infrastructure/interfaces
- Circular dependencies between layers
- Business logic in interface layer

**Action**: BLOCK commit, must fix before proceeding

### HIGH
- Application layer importing concrete infrastructure
- Interface layer importing infrastructure directly
- Layer bypassing dependency inversion

**Action**: WARN, should fix before merge

### MEDIUM
- Non-standard file organization
- Missing interfaces for infrastructure
- Inconsistent naming conventions

**Action**: INFO, fix when convenient

### LOW
- Import order violations
- Missing documentation
- Suboptimal patterns

**Action**: LOG, technical debt tracking

## Validation Algorithms

### Import Analysis Algorithm

```
1. FOR each source file:
   a. Determine layer from file path
   b. Extract all import statements
   c. Categorize imports by target layer

2. FOR each import:
   a. Check if import violates layer rules
   b. If violation:
      - Determine severity
      - Generate fix recommendation
      - Log violation with file:line

3. Aggregate violations by severity
4. Generate report with actionable fixes
```

### Circular Dependency Detection

```
1. Build import graph: file → [imported files]
2. Run depth-first search for cycles
3. FOR each cycle found:
   a. Identify shortest cycle path
   b. Suggest interface extraction
   c. Report with file:line for each link in cycle
```

### Anti-Pattern Detection

```
1. FOR each architectural anti-pattern:
   a. Define detection pattern (regex, AST analysis)
   b. Scan files for pattern matches
   c. Classify matches by severity

2. Common anti-patterns:
   - Business logic in presentation (detect DB calls in controllers)
   - Domain importing infrastructure (import analysis)
   - Missing dependency inversion (concrete types in constructors)
```

## Customization

### Custom Rule Definition Format

**arch-rules.yaml:**
```yaml
# Architecture pattern
architecture: clean  # or hexagonal, layered, mvc

# Layer definitions
layers:
  domain:
    paths:
      - src/domain
      - src/core
    can_import:
      - domain
    cannot_import:
      - application
      - infrastructure
      - interfaces

  application:
    paths:
      - src/application
      - src/usecases
    can_import:
      - domain
      - application
    cannot_import:
      - interfaces
      - infrastructure  # concrete implementations

  infrastructure:
    paths:
      - src/infrastructure
      - src/adapters
    can_import:
      - domain
      - application
    cannot_import:
      - interfaces

  interface:
    paths:
      - src/interfaces
      - src/api
    can_import:
      - application
      - domain  # for types only
    cannot_import:
      - infrastructure

# Severity mappings
severity:
  domain_importing_infrastructure: CRITICAL
  application_importing_interfaces: HIGH
  circular_dependency: CRITICAL
  business_logic_in_interface: CRITICAL
  missing_dependency_inversion: MEDIUM

# Exceptions (patterns to ignore)
exceptions:
  - pattern: "from typing import"
    reason: "Standard library, not architectural concern"

  - pattern: "from dataclasses import"
    reason: "Python built-in, not layer violation"

  - pattern: "import pytest"
    reason: "Test infrastructure"

# File patterns to scan
file_patterns:
  - "**/*.py"
  - "**/*.js"
  - "**/*.ts"

# File patterns to exclude
exclude_patterns:
  - "**/node_modules/**"
  - "**/.venv/**"
  - "**/tests/**"
  - "**/__pycache__/**"
```

### Running with Custom Rules

```bash
# Use custom rules file
python validate.py --rules custom-arch-rules.yaml

# Override specific settings
python validate.py --architecture hexagonal --strict

# Validate specific directories only
python validate.py --paths src/domain src/application
```

## Error Messages and Fixes

### Error: Domain Importing Infrastructure

**Message:**
```
❌ [CRITICAL] Domain Layer Importing Infrastructure
File: src/domain/models/user.py:5
Code: from infrastructure.database import DatabaseConnection
```

**Fix:**
```python
# BEFORE (domain/models/user.py)
from infrastructure.database import DatabaseConnection

class User:
    def save(self):
        db = DatabaseConnection()
        db.execute(...)

# AFTER (domain/repositories/user_repository.py)
from typing import Protocol

class UserRepository(Protocol):
    def save(self, user: User) -> None: ...

# AFTER (domain/models/user.py)
# No database imports!

# AFTER (infrastructure/repositories/user_repository_impl.py)
from domain.repositories import UserRepository
from infrastructure.database import DatabaseConnection

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def save(self, user: User) -> None:
        self.db.execute(...)
```

### Error: Application Importing Interfaces

**Message:**
```
❌ [HIGH] Application Importing Interface Layer
File: src/application/services/search.py:3
Code: from interfaces.api.routes import SearchEndpoint
```

**Fix:**
```python
# BEFORE (application/services/search.py)
from interfaces.api.routes import SearchEndpoint

class SearchService:
    def __init__(self):
        self.endpoint = SearchEndpoint()

# AFTER (application/handlers/search_handler.py)
class SearchHandler:
    def handle(self, query: SearchQuery) -> SearchResult:
        # Application logic here
        return SearchResult(...)

# AFTER (interfaces/api/routes.py)
from application.handlers import SearchHandler

@app.post("/search")
def search(query: str):
    handler = SearchHandler()
    return handler.handle(SearchQuery(query))
```

### Error: Circular Dependency

**Message:**
```
❌ [CRITICAL] Circular Dependency Detected
Cycle: service_a.py → service_b.py → service_a.py
Files involved:
  - src/services/service_a.py:12
  - src/services/service_b.py:8
```

**Fix:**
```python
# BEFORE
# service_a.py
from service_b import ServiceB

class ServiceA:
    def __init__(self):
        self.service_b = ServiceB()

# service_b.py
from service_a import ServiceA

class ServiceB:
    def __init__(self):
        self.service_a = ServiceA()

# AFTER - Extract interface
# service_interface.py
from typing import Protocol

class ServiceInterface(Protocol):
    def execute(self) -> Result: ...

# service_a.py
from service_interface import ServiceInterface

class ServiceA:
    def __init__(self, dependency: ServiceInterface):
        self.dependency = dependency

# service_b.py
from service_interface import ServiceInterface

class ServiceB:
    def __init__(self, dependency: ServiceInterface):
        self.dependency = dependency
```

## Performance Considerations

### Optimization Strategies

**1. Incremental Validation**
- Only validate changed files in git diff
- Cache validation results by file hash
- Skip unchanged files

**2. Parallel Processing**
- Scan files in parallel (use multiprocessing)
- Aggregate results after parallel scan
- Target: <2s for 1000+ files

**3. Smart Filtering**
- Exclude test files (unless specifically requested)
- Skip generated files (migrations, compiled, etc.)
- Use .gitignore patterns

**4. Caching**
- Cache import graph per file
- Invalidate on file modification
- Store in `.arch-validation-cache/`

### Expected Performance

| Codebase Size | Files | Validation Time |
|--------------|-------|-----------------|
| Small        | <100  | <0.5s          |
| Medium       | 100-500 | 0.5-1.5s     |
| Large        | 500-2000 | 1.5-3s      |
| Very Large   | 2000+ | 3-5s           |

## Integration Examples

### Pre-Commit Hook

**.git/hooks/pre-commit:**
```bash
#!/bin/bash

echo "Running architecture validation..."

# Get staged Python files
FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.py$')

if [ -z "$FILES" ]; then
    echo "No Python files to validate"
    exit 0
fi

# Run validation on staged files only
python .claude/skills/validate-architecture/scripts/validate.py --files $FILES --strict

if [ $? -ne 0 ]; then
    echo "❌ Architecture validation failed!"
    echo "Fix violations or use --no-verify to bypass (not recommended)"
    exit 1
fi

echo "✅ Architecture validation passed"
exit 0
```

### GitHub Actions

**.github/workflows/architecture.yml:**
```yaml
name: Architecture Validation

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Validate Architecture
        run: |
          python .claude/skills/validate-architecture/scripts/validate.py --strict

      - name: Comment on PR
        if: failure() && github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ Architecture validation failed. See logs for details.'
            })
```

### VSCode Extension

**settings.json:**
```json
{
  "emeraldwalk.runonsave": {
    "commands": [
      {
        "match": "\\.py$",
        "cmd": "python .claude/skills/validate-architecture/scripts/validate.py --file ${file}"
      }
    ]
  }
}
```

## Further Reading

- **Clean Architecture** by Robert C. Martin
- **Hexagonal Architecture** by Alistair Cockburn
- **Domain-Driven Design** by Eric Evans
- **Architecture Decision Records**: docs/adr/
