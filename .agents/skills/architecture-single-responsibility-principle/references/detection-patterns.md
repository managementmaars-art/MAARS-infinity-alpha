# Detection Patterns - AST Patterns and Metrics

## Multi-Dimensional Detection Strategy

SRP violations are detected using multiple independent signals, each with a confidence score. Violations with multiple signals have higher confidence.

## Detection Dimensions

### 1. Naming Patterns (40% Confidence)

**Signal**: Method or class names indicate multiple responsibilities.

#### Pattern 1.1: Method Names with "and"

```yaml
id: method-name-and
language: python
rule:
  pattern: "def $NAME_and_$REST"
```

**Detection**:
```bash
# Using ast-grep
mcp__ast-grep__find_code(
  pattern="def $NAME_and_$REST",
  language="python",
  project_folder="/path/to/project"
)
```

**Examples**:
```python
# ❌ Violations
def validate_and_save_user(user: User):  # 40% confidence violation
    pass

def fetch_and_process_data(data_id: str):  # 40% confidence violation
    pass

def create_and_index_document(doc: Document):  # 40% confidence violation
    pass
```

**Fix Guidance**:
```python
# ✅ Split into separate methods
def validate_user(user: User) -> ServiceResult[User]:
    pass

def save_user(user: User) -> ServiceResult[None]:
    pass

# Or use orchestrator pattern
def create_user_workflow(user: User) -> ServiceResult[User]:
    validated = self.validate_user(user)
    if not validated.success:
        return validated
    return self.save_user(validated.value)
```

#### Pattern 1.2: Class Names Indicating Multiple Actors

```yaml
id: class-name-multiple-actors
language: python
rule:
  any:
    - pattern: "class $NAMEManager"
    - pattern: "class $NAMEHandler"
    - pattern: "class $NAMEUtils"
    - pattern: "class $NAMEHelper"
```

**Examples**:
```python
# ❌ Red flags (review needed)
class UserManager:  # What does it manage? Vague
    pass

class DataHandler:  # Handles what? Vague
    pass

class Utils:  # Multiple unrelated utilities
    pass
```

**Fix Guidance**: Rename with specific actor/responsibility.

```python
# ✅ Specific actor names
class UserValidator:  # Validates users
    pass

class UserRepository:  # Persists users
    pass

class DateFormatter:  # Formats dates (not "DateUtils")
    pass
```

---

### 2. Size Metrics (60% Confidence)

**Signal**: Large classes/methods likely serve multiple actors.

#### Metric 2.1: Class Size (Lines of Code)

**Thresholds**:
- **300-500 lines**: Review needed (40% confidence)
- **500-1000 lines**: Warning (60% confidence)
- **>1000 lines**: Critical (80% confidence)

**Detection**:
```python
import ast

def analyze_class_size(file_path: str) -> dict:
    with open(file_path) as f:
        tree = ast.parse(f.read())

    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            lines = node.end_lineno - node.lineno + 1
            confidence = 0.0
            if lines > 1000:
                confidence = 0.8
            elif lines > 500:
                confidence = 0.6
            elif lines > 300:
                confidence = 0.4

            if confidence > 0:
                results.append({
                    "class": node.name,
                    "lines": lines,
                    "confidence": confidence,
                    "start_line": node.lineno
                })

    return results
```

**Fix Guidance**: Split into multiple classes by actor.

#### Metric 2.2: Method Count

**Thresholds**:
- **15-20 methods**: Review needed (40% confidence)
- **20-30 methods**: Warning (60% confidence)
- **>30 methods**: Critical (80% confidence)

**Detection**:
```python
def count_class_methods(file_path: str) -> dict:
    with open(file_path) as f:
        tree = ast.parse(f.read())

    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            public_methods = [m for m in methods if not m.name.startswith("_")]

            confidence = 0.0
            if len(methods) > 30:
                confidence = 0.8
            elif len(methods) > 20:
                confidence = 0.6
            elif len(methods) > 15:
                confidence = 0.4

            if confidence > 0:
                results.append({
                    "class": node.name,
                    "total_methods": len(methods),
                    "public_methods": len(public_methods),
                    "confidence": confidence
                })

    return results
```

#### Metric 2.3: Method Size (Lines of Code)

**Thresholds**:
- **50-100 lines**: Review needed (40% confidence)
- **100-200 lines**: Warning (60% confidence)
- **>200 lines**: Critical (80% confidence)

**Detection**:
```bash
# Using ast-grep to find long methods
mcp__ast-grep__find_code_by_rule(
  yaml="""
id: long-method
language: python
rule:
  pattern: |
    def $NAME($$$PARAMS):
      $$$BODY
""",
  project_folder="/path/to/project"
)

# Then analyze line count for each match
```

---

### 3. Dependency Analysis (75% Confidence)

**Signal**: Many constructor dependencies suggest multiple actors.

#### Metric 3.1: Constructor Parameter Count

**Thresholds**:
- **5-8 parameters**: Warning (75% confidence)
- **>8 parameters**: Critical (90% confidence)

**Detection**:
```yaml
id: constructor-many-params
language: python
rule:
  pattern: |
    def __init__(self, $$$PARAMS):
      $$$BODY
  constraints:
    PARAMS:
      count: { min: 5 }
```

**Examples**:
```python
# ❌ Too many dependencies (90% confidence violation)
class UserService:
    def __init__(
        self,
        validator: UserValidator,
        repository: UserRepository,
        email_sender: EmailSender,
        logger: Logger,
        metrics: MetricsCollector,
        cache: Cache,
        config: Config,
        event_bus: EventBus,
        notifier: Notifier
    ):
        # 9 dependencies → likely serving 9 different actors
        pass
```

**Fix Guidance**: Split into multiple services.

```python
# ✅ Split by actor
class UserValidationService:
    def __init__(self, validator: UserValidator, logger: Logger):
        # Validation actor
        pass

class UserPersistenceService:
    def __init__(self, repository: UserRepository, cache: Cache):
        # Persistence actor
        pass

class UserNotificationService:
    def __init__(self, email_sender: EmailSender, notifier: Notifier):
        # Communication actor
        pass
```

---

### 4. Complexity Metrics (60-80% Confidence)

**Signal**: High complexity indicates multiple logical branches (actors).

#### Metric 4.1: Cyclomatic Complexity

**Thresholds** (per method):
- **10-15**: Warning (60% confidence)
- **>15**: Critical (75% confidence)

**Detection** (requires radon):
```bash
# Using radon
radon cc path/to/file.py -a -nc

# Output:
# file.py
#     M 45:4 UserService.validate_and_save - D (15)
#     M 78:4 UserService.process_workflow - F (22)
```

**Interpretation**:
- **A-B (1-10)**: Low complexity, likely single responsibility
- **C-D (11-20)**: Moderate complexity, review needed
- **E-F (>20)**: High complexity, likely SRP violation

**Fix Guidance**: Extract complex branches into separate methods/classes.

#### Metric 4.2: God Class Detection (ATFD + WMC + TCC)

**Formula**: God class if ALL true:
- **ATFD** (Access to Foreign Data) **>5**: Accesses many external classes
- **WMC** (Weighted Methods per Class) **>47**: High total complexity
- **TCC** (Tight Class Cohesion) **<0.33**: Low internal cohesion

**Confidence**: 80% if all three metrics violated

**Detection** (requires pylint or custom analysis):
```bash
# Using pylint
pylint path/to/file.py --disable=all --enable=too-many-instance-attributes,too-many-public-methods

# Custom ATFD calculation
# Count external class accesses in methods
```

**ATFD Calculation**:
```python
def calculate_atfd(class_node: ast.ClassDef) -> int:
    """Count accesses to foreign (external) data."""
    foreign_accesses = set()

    for method in [n for n in class_node.body if isinstance(n, ast.FunctionDef)]:
        for node in ast.walk(method):
            if isinstance(node, ast.Attribute):
                # Check if accessing external object
                if isinstance(node.value, ast.Name) and node.value.id != "self":
                    foreign_accesses.add((node.value.id, node.attr))

    return len(foreign_accesses)
```

**WMC Calculation**:
```python
def calculate_wmc(class_node: ast.ClassDef) -> int:
    """Sum of cyclomatic complexities of all methods."""
    total_complexity = 0

    for method in [n for n in class_node.body if isinstance(n, ast.FunctionDef)]:
        complexity = calculate_cyclomatic_complexity(method)
        total_complexity += complexity

    return total_complexity
```

**TCC Calculation**:
```python
def calculate_tcc(class_node: ast.ClassDef) -> float:
    """Ratio of method pairs that share instance variables."""
    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]

    if len(methods) < 2:
        return 1.0

    # Find which instance variables each method uses
    method_vars = {}
    for method in methods:
        used_vars = set()
        for node in ast.walk(method):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == "self":
                    used_vars.add(node.attr)
        method_vars[method.name] = used_vars

    # Count pairs that share at least one variable
    total_pairs = 0
    connected_pairs = 0

    for i, method1 in enumerate(methods):
        for method2 in methods[i+1:]:
            total_pairs += 1
            if method_vars[method1.name] & method_vars[method2.name]:
                connected_pairs += 1

    return connected_pairs / total_pairs if total_pairs > 0 else 1.0
```

**Example Detection**:
```python
# ❌ God Class (80% confidence)
class UserService:
    # ATFD = 12 (accesses repository, cache, email, logger, metrics, etc.)
    # WMC = 65 (high total complexity across 20 methods)
    # TCC = 0.15 (methods don't share instance variables)

    def __init__(self, ...):  # 9 dependencies
        pass

    def create_user(self):  # Complexity: 8
        pass

    def validate_user(self):  # Complexity: 6
        pass

    # ... 18 more methods
```

**Fix Guidance**: Split into cohesive classes.

```python
# ✅ Split by cohesion
class UserValidator:
    # ATFD = 1, WMC = 12, TCC = 0.8
    # All methods share validation rules
    pass

class UserRepository:
    # ATFD = 2, WMC = 8, TCC = 0.9
    # All methods share database connection
    pass
```

---

### 5. Project-Specific Patterns (90% Confidence)

**Signal**: Violations of project-specific architectural rules.

#### Pattern 5.1: Optional Config Parameters

```yaml
id: optional-config-anti-pattern
language: python
rule:
  pattern: "$NAME: $TYPE | None = None"
  inside:
    kind: function_definition
    pattern: "def __init__"
```

**Examples**:
```python
# ❌ CRITICAL violation (90% confidence)
class UserService:
    def __init__(
        self,
        settings: Settings | None = None,  # Violates fail-fast AND SRP
        logger: Logger | None = None
    ):
        self.settings = settings or Settings()  # Creates default
        # Now serves two actors: configured mode + default mode
```

**Fix Guidance**: Require configuration injection.

```python
# ✅ CORRECT
class UserService:
    def __init__(self, settings: Settings, logger: Logger):
        if not settings:
            raise ValueError("settings required")
        if not logger:
            raise ValueError("logger required")
        self.settings = settings
        self.logger = logger
```

#### Pattern 5.2: Domain Entities Doing I/O

```yaml
id: domain-entity-io
language: python
rule:
  any:
    - pattern: |
        class $NAME:
          $$$BODY
          def save(self):
            $$$
    - pattern: |
        class $NAME:
          $$$BODY
          def fetch(self):
            $$$
  inside:
    path: "src/**/domain/**/*.py"
```

**Examples**:
```python
# ❌ CRITICAL violation (90% confidence)
# File: src/domain/entities/user.py
class User:
    def __init__(self, name: str):
        self.name = name

    def save(self):
        # Domain entity doing persistence!
        # Violates Clean Architecture AND SRP
        db.execute("INSERT INTO users ...")
```

**Fix Guidance**: Move I/O to infrastructure layer.

```python
# ✅ CORRECT
# File: src/domain/entities/user.py
class User:
    def __init__(self, name: str):
        self.name = name
    # No I/O methods

# File: src/infrastructure/repositories/user_repository.py
class Neo4jUserRepository:
    def save(self, user: User) -> ServiceResult[None]:
        # Infrastructure layer handles I/O
        pass
```

#### Pattern 5.3: Application Services with Business Logic

```yaml
id: application-service-business-logic
language: python
rule:
  pattern: |
    class $NAMEService:
      $$$BODY
      def $METHOD(self):
        if $CONDITION:
          $$$
  inside:
    path: "src/**/application/**/*.py"
  constraints:
    CONDITION:
      # Look for business rules (e.g., age >= 18, amount > 100)
      regex: "(>=|<=|>|<)\\s*\\d+"
```

**Examples**:
```python
# ❌ WARNING violation (70% confidence)
# File: src/application/services/user_service.py
class UserService:
    def create_user(self, data: dict) -> ServiceResult[User]:
        # Business logic in application layer!
        if data["age"] >= 18:  # Business rule here
            user = User(data["name"])
            return self.repository.save(user)
        return ServiceResult.failure("User must be adult")
```

**Fix Guidance**: Move business logic to domain layer.

```python
# ✅ CORRECT
# File: src/domain/entities/user.py
class User:
    def __init__(self, name: str, age: int):
        if age < 18:
            raise ValueError("User must be adult")  # Business rule in domain
        self.name = name
        self.age = age

# File: src/application/services/user_service.py
class UserService:
    def create_user(self, data: dict) -> ServiceResult[User]:
        # Just orchestration
        try:
            user = User(data["name"], data["age"])  # Domain validates
            return self.repository.save(user)
        except ValueError as e:
            return ServiceResult.failure(str(e))
```

---

## Confidence Scoring

### Single Signal Detection

| Signal | Confidence | Action |
|--------|-----------|---------|
| Method name with "and" | 40% | Review |
| Class >300 lines | 40% | Review |
| Class >15 methods | 40% | Review |
| Method >50 lines | 40% | Review |
| Class >500 lines | 60% | Warning |
| Method >100 lines | 60% | Warning |
| Constructor >5 params | 75% | Warning |
| Cyclomatic complexity >10 | 60% | Warning |
| God class (ATFD+WMC+TCC) | 80% | Critical |
| Constructor >8 params | 90% | Critical |
| Optional config parameter | 90% | Critical |
| Domain entity I/O | 90% | Critical |

### Multi-Signal Detection (Additive)

When multiple signals detected, confidence increases:

```
Combined Confidence = 1 - (1 - C1) × (1 - C2) × ... × (1 - Cn)
```

**Example**:
```python
class UserService:
    # Signal 1: Method name "validate_and_save" → 40%
    # Signal 2: Class 450 lines → 60%
    # Signal 3: 18 methods → 40%
    # Signal 4: 7 constructor params → 75%

    # Combined: 1 - (0.6 × 0.4 × 0.6 × 0.25) = 1 - 0.036 = 96.4% confidence
    # → CRITICAL violation
```

---

## Detection Performance

### Fast Level (5-10s)
- Naming patterns (ast-grep)
- Basic size metrics (line counts)
- Constructor param counts

**Coverage**: ~60% of violations

### Thorough Level (30s)
- All Fast checks
- Cyclomatic complexity (radon)
- Project-specific patterns

**Coverage**: ~85% of violations

### Full Level (1-2min)
- All Thorough checks
- God class metrics (ATFD, WMC, TCC)
- Actor analysis

**Coverage**: ~95% of violations

---

## False Positive Mitigation

### 1. Whitelisting

Some patterns are intentional:

```python
# Whitelist: Facade pattern (intentional aggregation)
@whitelist_srp
class UserServiceFacade:
    """Public API facade - intentionally aggregates."""
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
```

### 2. Context-Aware Detection

Consider file location:

- **Domain layer**: Strict SRP (business logic only)
- **Application layer**: Orchestration allowed
- **Interface layer**: Facades allowed
- **Tests**: Helpers allowed

### 3. Confidence Thresholds

Report only high-confidence violations:

- **Critical (>80%)**: Always report
- **Warning (60-80%)**: Report in thorough/full
- **Review (40-60%)**: Report in full only

---

## Summary

### Detection Dimensions
1. **Naming**: "and" in names, vague names (40% confidence)
2. **Size**: Class/method line counts (40-60% confidence)
3. **Dependencies**: Constructor params (75-90% confidence)
4. **Complexity**: Cyclomatic, God class metrics (60-80% confidence)
5. **Project Patterns**: Optional config, layer violations (90% confidence)

### Confidence Scoring
- Single signals: 40-90% confidence
- Multiple signals: Combined (additive)
- >80%: Critical violations
- 60-80%: Warnings
- 40-60%: Review needed

### Performance
- Fast (5-10s): Naming + size
- Thorough (30s): + Complexity + patterns
- Full (1-2min): + God class + actor analysis

### False Positives
- Whitelisting for intentional patterns
- Context-aware (layer-specific rules)
- Confidence thresholds
