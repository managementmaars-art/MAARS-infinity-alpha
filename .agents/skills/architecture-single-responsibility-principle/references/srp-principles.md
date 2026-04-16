# SRP Principles - Core Concepts

## Definition

> "A module should be responsible to one, and only one, actor."
> — Robert C. Martin (Uncle Bob)

**Key Insight**: SRP is **actor-driven**, not task-driven. A class can do many things, but those things should serve only one actor (user, stakeholder, or system component).

## Actor-Driven vs Task-Driven

### ❌ WRONG: Task-Driven Thinking

```python
# "This class does too many things"
class UserService:
    def validate_user(self):  # Task 1
        pass

    def save_user(self):      # Task 2
        pass

    def send_email(self):     # Task 3
        pass
```

**Problem**: Counting tasks doesn't identify the real issue.

### ✅ CORRECT: Actor-Driven Thinking

```python
# "This class serves three different actors"
class UserService:
    def validate_user(self):  # Actor: Business rules team
        pass

    def save_user(self):      # Actor: Database team
        pass

    def send_email(self):     # Actor: Communications team
```

**Solution**: Split by actor, not by task count.

```python
# Serve Business Rules actor
class UserValidator:
    def validate(self, user: User) -> ServiceResult[User]:
        pass

# Serve Database actor
class UserRepository:
    def save(self, user: User) -> ServiceResult[None]:
        pass

# Serve Communications actor
class UserNotifier:
    def send_welcome_email(self, user: User) -> ServiceResult[None]:
        pass
```

## Why SRP Matters

### 1. Change Isolation

**With SRP violation**:
```python
class UserService:
    def validate_and_save_user(self):
        # Business rules change → Database team affected
        # Database schema change → Business rules team affected
        pass
```

**With SRP compliance**:
```python
class UserValidator:
    def validate(self):
        # Business rules change → Only this class changes
        pass

class UserRepository:
    def save(self):
        # Database schema change → Only this class changes
        pass
```

### 2. Testing Simplicity

**With SRP violation**:
```python
# Test requires: mock database, mock email server, mock validator
def test_user_service():
    mock_db = MagicMock()
    mock_email = MagicMock()
    mock_validator = MagicMock()
    service = UserService(mock_db, mock_email, mock_validator)
    # Complex setup for every test
```

**With SRP compliance**:
```python
# Test requires: only what this class needs
def test_user_validator():
    validator = UserValidator()
    result = validator.validate(user)
    assert result.success
```

### 3. Reusability

**With SRP violation**:
```python
# Can't reuse validation without bringing database logic
service = UserService(db, email, validator)
service.validate_user()  # But this pulls in database dependency
```

**With SRP compliance**:
```python
# Validation is standalone
validator = UserValidator()
result = validator.validate(user)  # No database dependency
```

## Common Misconceptions

### Misconception 1: "One Method = One Responsibility"

❌ **WRONG**:
```python
# This is NOT good SRP (too granular)
class User:
    def get_first_name(self): pass
    def get_last_name(self): pass
    def get_full_name(self): pass  # Violation?
```

✅ **CORRECT**:
```python
# All serve the same actor (UI/presentation)
class User:
    def get_first_name(self): return self._first_name
    def get_last_name(self): return self._last_name
    def get_full_name(self): return f"{self.first_name} {self.last_name}"
    # All serve the same actor → SRP compliant
```

### Misconception 2: "Private Methods Count as Responsibilities"

❌ **WRONG**:
```python
# "This class has 10 methods, must be SRP violation"
class UserValidator:
    def validate(self, user: User) -> ServiceResult[User]:
        self._check_name(user.name)
        self._check_email(user.email)
        self._check_age(user.age)
        # ...

    def _check_name(self, name: str): pass
    def _check_email(self, email: str): pass
    def _check_age(self, age: int): pass
    # ...
```

✅ **CORRECT**:
```python
# One public interface (validate) → One actor (validation rules)
# Private methods are implementation details
# SRP compliant
```

### Misconception 3: "Utility Classes Are Fine"

❌ **WRONG**:
```python
# "Utils" is a code smell, not a responsibility
class Utils:
    def format_date(self): pass
    def send_email(self): pass
    def validate_password(self): pass
    # Serves multiple actors → SRP violation
```

✅ **CORRECT**:
```python
# Split by actor
class DateFormatter:  # Serves presentation actor
    def format(self, date): pass

class EmailSender:    # Serves communication actor
    def send(self, email): pass

class PasswordValidator:  # Serves security actor
    def validate(self, password): pass
```

## Actor Identification Questions

Use these to identify actors:

1. **Who requests changes to this code?**
   - Business analyst → Business rules actor
   - DBA → Database actor
   - Ops team → Infrastructure actor

2. **What causes this code to change?**
   - Validation rules change → Validation actor
   - API contract change → API actor
   - Performance requirements → Performance actor

3. **Who owns the requirements?**
   - Product team → Business logic actor
   - Platform team → Infrastructure actor
   - Security team → Security actor

## SRP in Clean Architecture

### Domain Layer
**Actor**: Business rules

```python
# ✅ GOOD: Single actor (business rules)
class User:
    def __init__(self, name: str, email: str):
        self._name = name
        self._email = email

    def is_adult(self) -> bool:
        return self.age >= 18  # Business rule
```

❌ **BAD**: Multiple actors
```python
class User:
    def save_to_database(self):  # Actor: Database team
        pass

    def send_welcome_email(self):  # Actor: Communications team
        pass
```

### Application Layer
**Actor**: Use case workflow

```python
# ✅ GOOD: Single use case
class CreateUserHandler:
    def handle(self, command: CreateUserCommand) -> ServiceResult[User]:
        # Orchestrate one use case
        user = self._validator.validate(command.data)
        saved_user = self._repository.save(user)
        self._notifier.notify(saved_user)
        return ServiceResult.success(saved_user)
```

❌ **BAD**: Multiple use cases
```python
class UserHandler:
    def create_user(self): pass  # Use case 1
    def update_user(self): pass  # Use case 2
    def delete_user(self): pass  # Use case 3
    # Multiple actors (create workflow, update workflow, delete workflow)
```

### Infrastructure Layer
**Actor**: External system

```python
# ✅ GOOD: Single external system
class Neo4jUserRepository:
    def save(self, user: User) -> ServiceResult[None]:
        # Only talks to Neo4j
        pass

    def find_by_id(self, user_id: str) -> ServiceResult[User | None]:
        # Only talks to Neo4j
        pass
```

❌ **BAD**: Multiple external systems
```python
class UserRepository:
    def save_to_neo4j(self, user): pass     # System 1: Neo4j
    def cache_in_redis(self, user): pass    # System 2: Redis
    def index_in_elasticsearch(self, user): pass  # System 3: Elasticsearch
    # Multiple actors (Neo4j team, Redis team, Elasticsearch team)
```

## SRP and SOLID

SRP is the foundation of SOLID:

- **S**ingle Responsibility → Classes change for one reason
- **O**pen/Closed → Easy to extend when responsibilities are isolated
- **L**iskov Substitution → Easier to substitute when responsibilities are clear
- **I**nterface Segregation → Natural when each actor has minimal interface
- **D**ependency Inversion → Dependencies flow from actors, not implementations

**SRP enables the other four principles.**

## Red Flags for SRP Violations

1. **Class names with "and", "or", "manager", "handler", "utils"**
   - `UserAndOrderService` → Two actors (users, orders)
   - `DataManager` → Vague responsibility

2. **Method names with "and"**
   - `validate_and_save()` → Two actors (validation, persistence)
   - `fetch_and_process()` → Two actors (retrieval, processing)

3. **Many constructor dependencies (>4)**
   - Suggests serving multiple actors
   - Each dependency might represent a different actor

4. **Long classes (>300 lines) or many methods (>15)**
   - Likely serving multiple actors
   - Natural split points exist

5. **Optional configuration parameters**
   - `config: Config | None = None` → Violates fail-fast AND SRP
   - Creates multiple code paths → multiple actors

6. **God classes (high coupling, low cohesion)**
   - ATFD >5 (accesses many external classes)
   - WMC >47 (high complexity)
   - TCC <0.33 (low cohesion)

## When NOT to Split

### 1. Cohesive Private Methods

```python
# ✅ GOOD: Don't split
class UserValidator:
    def validate(self, user: User) -> ServiceResult[User]:
        self._check_name(user.name)
        self._check_email(user.email)
        self._check_age(user.age)
        return ServiceResult.success(user)

    def _check_name(self, name: str): pass
    def _check_email(self, email: str): pass
    def _check_age(self, age: int): pass
```

**Reason**: All serve one actor (validation rules), private methods are implementation.

### 2. Facade Pattern (Intentional)

```python
# ✅ GOOD: Intentional facade
class UserServiceFacade:
    """Simplified interface for external consumers."""
    def create_user(self, data: dict) -> ServiceResult[User]:
        validated = self._validator.validate(data)
        saved = self._repository.save(validated)
        self._notifier.notify(saved)
        return ServiceResult.success(saved)
```

**Reason**: Actor is "external API consumer", orchestration is the responsibility.

### 3. Data Transfer Objects

```python
# ✅ GOOD: Don't split
@dataclass(frozen=True)
class UserDTO:
    user_id: str
    name: str
    email: str
    created_at: datetime

    def to_dict(self) -> dict: pass
    def from_dict(cls, data: dict): pass
```

**Reason**: Single actor (data transfer), methods support that responsibility.

## Summary

- **SRP = One Actor**: Classes change when one actor's requirements change
- **Not task count**: Many methods can serve one actor
- **Identify actors**: Who requests changes? What causes changes?
- **Clean Architecture**: Each layer serves specific actor types
- **Red flags**: "and" in names, many dependencies, God classes
- **Don't over-split**: Cohesive helpers, facades, DTOs are fine

**Remember**: The goal is to isolate reasons for change, not to minimize method count.
