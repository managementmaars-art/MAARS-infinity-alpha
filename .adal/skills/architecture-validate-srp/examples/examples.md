# SRP Validation Examples

Complete working examples demonstrating SRP violations and correct implementations.

## Example Files

### 1. Naming Pattern Violations
**File:** [violation-naming-patterns.py](./violation-naming-patterns.py)

Demonstrates:
- Methods with "and" in name (40% confidence violation)
- Multiple actors in single class
- Correct split by actor

**Key violations:**
- `validate_and_save_user()` - serves 2 actors
- `Employee` class - serves 3 actors (Accounting, HR, DBA)

**Fixes shown:**
- Split into `validate_user()` and `save_user()`
- Split into `PayCalculator`, `HourReporter`, `EmployeeRepository`

---

### 2. God Class Violations
**File:** [violation-god-class.py](./violation-god-class.py)

Demonstrates:
- Constructor with 8+ parameters (God Class indicator)
- Low cohesion across methods
- Multiple actor domains

**Key violations:**
- `UserService` with 9 dependencies serving 5+ actors

**Fixes shown:**
- Split into `UserAuthService` (Security)
- Split into `UserNotificationService` (Communication)
- Split into `UserAnalytics` (Analytics)

---

### 3. Correct Single Actor Implementation
**File:** [correct-single-actor.py](./correct-single-actor.py)

Demonstrates:
- Multiple methods serving single actor (SRP-compliant)
- High cohesion with shared instance variables
- Private helper methods serving same responsibility

**Key examples:**
- `PayrollCalculator` - 4 methods, 1 actor (Accounting)
- `InvoiceGenerator` - Many methods with high cohesion

---

## Running Validation

To validate these examples:

```bash
# Fast check (naming patterns only)
./scripts/validate-srp.sh examples/ --level=fast

# Thorough check (all metrics)
./scripts/validate-srp.sh examples/ --level=thorough

# Check specific file
./scripts/validate-srp.sh examples/violation-god-class.py
```

## Expected Results

### violation-naming-patterns.py
```
❌ 2 violations found:
1. validate_and_save_user() - method name contains 'and'
2. Employee class - 3 actors detected
```

### violation-god-class.py
```
❌ 1 critical violation:
1. UserService - God Class (9 constructor params, low cohesion)
```

### correct-single-actor.py
```
✅ All classes SRP-compliant
- PayrollCalculator: 1 actor (Accounting)
- InvoiceGenerator: 1 actor (Accounting), high cohesion (TCC: 0.85)
```

---

## Learning Path

1. **Start with naming patterns** - Easiest to spot and fix
2. **Review constructor dependencies** - Quick indicator of violations
3. **Calculate cohesion metrics** - Deeper validation
4. **Perform actor analysis** - Full understanding

---

**See Also:**
- [../references/srp-principles.md](../references/srp-principles.md) - Core SRP concepts
- [../SKILL.md](../SKILL.md) - Complete validation workflow
