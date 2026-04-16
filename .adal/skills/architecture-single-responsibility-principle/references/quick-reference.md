# Quick Reference - SRP Validation Cheat Sheet

## One-Page SRP Checklist

### Definition

> **"A module should be responsible to one, and only one, actor."**
>
> — Robert C. Martin

**Key**: Actor-driven, not task-driven. Many methods can serve one actor.

---

## Quick Detection (30 seconds)

### Red Flags Checklist

**Method Level**:
- [ ] Method name contains "and" → 40% confidence violation
- [ ] Method >50 lines → Review needed
- [ ] Method >100 lines → 60% confidence violation
- [ ] Cyclomatic complexity >10 → 60% confidence violation

**Class Level**:
- [ ] Class >300 lines → Review needed
- [ ] Class >500 lines → 60% confidence violation
- [ ] Class >15 methods → Review needed
- [ ] Class >20 methods → 60% confidence violation
- [ ] Constructor >5 params → 75% confidence violation
- [ ] Constructor >8 params → 90% confidence violation

**Naming**:
- [ ] Contains "Manager", "Handler", "Utils", "Helper" → Review
- [ ] Vague responsibility (DataProcessor, FileManager) → Review

**Project-Specific**:
- [ ] Optional config (`Type | None = None`) → 90% critical
- [ ] Try/except ImportError → 90% critical
- [ ] Bare None returns (no ServiceResult) → 80% critical
- [ ] Domain entity with I/O → 90% critical

---

## Actor Identification (2 minutes)

Ask these questions:

### 1. Who Requests Changes?

```
Business analyst    → Business rules actor
DBA                → Database actor
DevOps team        → Infrastructure actor
Security team      → Security actor
Product manager    → Use case actor
API consumers      → Interface actor
```

### 2. What Causes Changes?

```
Validation rules change    → Validation actor
Database schema change     → Persistence actor
API contract change        → API actor
Performance requirements   → Performance actor
Business rules change      → Domain logic actor
```

### 3. Count Distinct Actors

```
1 actor  → ✅ SRP compliant
2 actors → ⚠️  Consider splitting
3+ actors → ❌ SRP violation
```

---

## Layer-Specific Rules

### Domain Layer

| ✅ Allowed | ❌ Forbidden |
|-----------|-------------|
| Business logic | I/O operations |
| Domain entities | Database queries |
| Value objects | File system access |
| Business rules | Network calls |
| Domain services | Framework dependencies |
| Repository protocols | External service calls |

**Actor**: Business rules only

**Example**:
```python
# ✅ GOOD
class User:
    def is_adult(self) -> bool:
        return self.age >= 18  # Business rule

# ❌ BAD
class User:
    def save(self):  # I/O in domain!
        db.execute(...)
```

---

### Application Layer

| ✅ Allowed | ❌ Forbidden |
|-----------|-------------|
| Command/query handlers | Business logic |
| Orchestrators | Direct database queries |
| Use case execution | Multiple use cases per handler |
| DTO transformations | Infrastructure details |
| Workflow coordination | Default config creation |

**Actor**: One use case only

**Example**:
```python
# ✅ GOOD
class CreateUserHandler:
    def handle(self, cmd: CreateUserCommand):
        # One use case

# ❌ BAD
class UserHandler:
    def create(self): pass  # Use case 1
    def update(self): pass  # Use case 2
    def delete(self): pass  # Use case 3
```

---

### Infrastructure Layer

| ✅ Allowed | ❌ Forbidden |
|-----------|-------------|
| Repository implementations | Business logic |
| Database queries | Use case orchestration |
| External service adapters | Multiple external systems |
| File system operations | Domain logic |
| Network calls | Application workflows |

**Actor**: One external system only

**Example**:
```python
# ✅ GOOD
class Neo4jCodeRepository:
    # Only talks to Neo4j

# ❌ BAD
class Repository:
    def save_to_neo4j(self): pass
    def cache_in_redis(self): pass
    def index_in_elasticsearch(self): pass
```

---

### Interface Layer

| ✅ Allowed | ❌ Forbidden |
|-----------|-------------|
| MCP tool registrars | Business logic |
| API endpoints | Direct database access |
| CLI commands | Application workflows |
| Request/response DTOs | Use case orchestration |
| Intentional facades | Multiple operations per tool |

**Actor**: External consumer operation

**Example**:
```python
# ✅ GOOD
@mcp.tool()
async def search_code(query: str):
    # Single operation

# ❌ BAD
@mcp.tool()
async def manage_users(action: str, data: dict):
    # Multiple operations
```

---

## Common Violations

### Violation 1: Optional Config Parameters

**Detection**:
```python
# ❌ WRONG
def __init__(self, settings: Settings | None = None):
    self.settings = settings or Settings()
```

**Fix**:
```python
# ✅ CORRECT
def __init__(self, settings: Settings):
    if not settings:
        raise ValueError("settings required")
    self.settings = settings
```

**Confidence**: 90% (critical)

---

### Violation 2: Method Name with "and"

**Detection**:
```python
# ❌ WRONG
def validate_and_save_user(self, user: User):
    self.validate(user)
    self.save(user)
```

**Fix**:
```python
# ✅ CORRECT (split by actor)
def validate_user(self, user: User) -> ServiceResult[User]:
    # Validation actor
    pass

def save_user(self, user: User) -> ServiceResult[None]:
    # Persistence actor
    pass

# Or orchestrator
def create_user_workflow(self, user: User) -> ServiceResult[User]:
    # Workflow coordinator actor
    validated = self.validate_user(user)
    if not validated.success:
        return validated
    return self.save_user(validated.value)
```

**Confidence**: 40% (review)

---

### Violation 3: God Class

**Detection**:
```python
# ❌ WRONG
class UserService:
    # 450 lines, 23 methods, 9 constructor params
    # ATFD=12, WMC=65, TCC=0.15
    def __init__(self, validator, repository, email, ...):
        pass
```

**Fix**:
```python
# ✅ CORRECT (split by actor)
class UserValidator:
    # Validation actor
    def validate(self, user): pass

class UserRepository:
    # Persistence actor
    def save(self, user): pass

class UserNotifier:
    # Notification actor
    def notify(self, user): pass
```

**Confidence**: 80% (critical)

---

### Violation 4: Domain Entity I/O

**Detection**:
```python
# ❌ WRONG (file: src/domain/entities/user.py)
class User:
    def save(self):  # I/O in domain!
        db.execute("INSERT ...")
```

**Fix**:
```python
# ✅ CORRECT
# File: src/domain/entities/user.py
class User:
    # Pure domain logic, no I/O
    def is_adult(self) -> bool:
        return self.age >= 18

# File: src/infrastructure/repositories/user_repository.py
class Neo4jUserRepository:
    def save(self, user: User) -> ServiceResult[None]:
        # I/O in infrastructure layer
        pass
```

**Confidence**: 90% (critical)

---

### Violation 5: Try/Except ImportError

**Detection**:
```python
# ❌ WRONG
try:
    from radon import cc_visit
    HAS_RADON = True
except ImportError:
    HAS_RADON = False

def analyze(self):
    if HAS_RADON:  # Multiple code paths
        return cc_visit(code)
    else:
        return fallback()
```

**Fix**:
```python
# ✅ CORRECT
from radon import cc_visit  # Fail fast if missing

def analyze(self):
    return cc_visit(code)  # Single code path
```

**Confidence**: 90% (critical)

---

## Confidence Scoring

### Single Signal

| Signal | Confidence | Action |
|--------|-----------|---------|
| Method name "and" | 40% | Review |
| Class >300 lines | 40% | Review |
| Class >15 methods | 40% | Review |
| Method >50 lines | 40% | Review |
| Class >500 lines | 60% | Warning |
| Method >100 lines | 60% | Warning |
| Cyclomatic >10 | 60% | Warning |
| Constructor >5 params | 75% | Warning |
| God class metrics | 80% | Critical |
| Constructor >8 params | 90% | Critical |
| Optional config | 90% | Critical |
| Domain I/O | 90% | Critical |
| Try/except ImportError | 90% | Critical |

### Multi-Signal (Additive)

```
Combined = 1 - (1 - C1) × (1 - C2) × ... × (1 - Cn)

Example:
  Signal 1: 40%
  Signal 2: 60%
  Signal 3: 75%
  Combined: 1 - (0.6 × 0.4 × 0.25) = 94% → Critical
```

---

## Fix Strategy

### Step 1: Identify Actors (5 min)

1. List all methods in class
2. Group by "who would request changes to this?"
3. Each group = one actor
4. Count distinct actors

**Example**:
```
UserService:
  validate_user()     → Business rules actor
  save_user()         → Database actor
  send_email()        → Communications actor
  log_activity()      → Observability actor

Result: 4 actors → SRP violation
```

---

### Step 2: Plan Split (10 min)

Create one class per actor:

```
Actor 1 (Business rules) → UserValidator
Actor 2 (Database)       → UserRepository
Actor 3 (Communications) → UserNotifier
Actor 4 (Observability)  → ActivityLogger
```

---

### Step 3: Extract Classes (30 min - 2 hours)

1. Create new class for each actor
2. Move methods to appropriate class
3. Inject dependencies as needed
4. Update tests

**Use `multi-file-refactor` skill for token-efficient coordination**

---

### Step 4: Validate (10 min)

- [ ] Run quality gates (`run-quality-gates` skill)
- [ ] Verify tests pass
- [ ] Check type checking (pyright)
- [ ] Run SRP validation again (should show improvement)

---

## When NOT to Split

### Exemption 1: Cohesive Private Methods

```python
# ✅ Don't split
class UserValidator:
    def validate(self, user):  # Public interface
        self._check_name()     # Private helper
        self._check_email()    # Private helper
        self._check_age()      # Private helper

    # All serve one actor: validation rules
```

**Rule**: Private methods supporting single public interface are fine.

---

### Exemption 2: Intentional Facades

```python
# ✅ Don't split (intentional)
class UserServiceFacade:
    """Simplified API for external consumers."""

    def create_user(self, data):
        # Orchestrates multiple actors for convenience
        # Actor: External consumer (intentional aggregation)
        validated = self.validator.validate(data)
        saved = self.repository.save(validated)
        self.notifier.notify(saved)
        return saved
```

**Rule**: Interface layer facades are allowed if clearly documented.

---

### Exemption 3: Value Objects

```python
# ✅ Don't split
@dataclass(frozen=True)
class ContentHash:
    value: str

    def matches(self, other): pass
    def to_short_form(self): pass
    def to_dict(self): pass
    @classmethod
    def from_content(cls, content): pass

    # All serve one actor: hash representation
```

**Rule**: All methods serve same actor (data representation).

---

## Quick Commands

### Run SRP Validation

```bash
# Default: thorough validation
Skill(command: "single-responsibility-principle")

# Fast pre-commit check (5-10s)
Skill(command: "single-responsibility-principle --level=fast")

# Full analysis with actor identification (1-2min)
Skill(command: "single-responsibility-principle --level=full --format=json")

# Validate specific directory
Skill(command: "single-responsibility-principle --path=src/domain/")
```

---

### Detect Specific Patterns

```bash
# Find methods with "and"
mcp__ast-grep__find_code(
  pattern="def $NAME_and_$REST",
  language="python",
  project_folder="/path/to/project"
)

# Find optional config anti-pattern
mcp__ast-grep__find_code_by_rule(
  yaml="""
id: optional-config
language: python
rule:
  pattern: "$NAME: $TYPE | None = None"
  inside:
    kind: function_definition
    pattern: "def __init__"
""",
  project_folder="/path/to/project"
)

# Find god classes (>15 methods)
mcp__ast-grep__find_code_by_rule(
  yaml="""
id: god-class
language: python
rule:
  pattern: "class $NAME:\\n  $$$BODY"
  has:
    stopBy: end
    kind: function_definition
    count: { min: 15 }
""",
  project_folder="/path/to/project"
)
```

---

## Integration

### With `code-review` Skill

Add as Step 2 sub-check:

```markdown
## Step 2: Single Responsibility Review
- [ ] Run `single-responsibility-principle --level=fast`
- [ ] Address critical violations (>80% confidence)
- [ ] Document acceptable warnings
```

---

### With `validate-architecture` Skill

Enforce layer-specific SRP rules:

```python
# Domain layer: no I/O
# Application layer: one use case per handler
# Infrastructure layer: one external system per repository
# Interface layer: one operation per tool
```

---

### With `run-quality-gates` Skill

Add as quality gate:

```bash
# In check_all.sh or pre-commit hook
Skill(command: "single-responsibility-principle --level=fast")
# Block commit if critical violations (>80% confidence)
```

---

### With `multi-file-refactor` Skill

Coordinate SRP refactoring across files:

1. Identify God classes
2. Plan extraction strategy (actor-based)
3. Use MultiEdit for atomic refactoring
4. Update tests in parallel

---

## Summary

### Quick Checklist

1. **Method name "and"?** → Split by actor
2. **Class >300 lines?** → Review for actors
3. **Constructor >5 params?** → Likely multiple actors
4. **Optional config?** → Critical violation
5. **Domain entity I/O?** → Critical violation

### Time Estimates

- **Detection**: 30 seconds (fast) to 2 minutes (full)
- **Actor identification**: 5 minutes
- **Planning split**: 10 minutes
- **Implementation**: 30 minutes to 2 hours (depends on class size)
- **Validation**: 10 minutes

### Remember

- **Actor-driven, not task-driven**
- **One reason to change = one actor**
- **Private helpers are fine if cohesive**
- **Facades allowed in interface layer**
- **Critical violations (>80%) = immediate action**
