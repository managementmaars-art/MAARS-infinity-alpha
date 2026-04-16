# SRP Principles - Core Concepts

**Complete guide to Single Responsibility Principle (SRP) with actor-driven approach.**

---

## Table of Contents

1. [Definition](#definition)
2. [Actor-Driven vs Task-Driven](#actor-driven-vs-task-driven)
3. [Common Misconceptions](#common-misconceptions)
4. [Identifying Actors](#identifying-actors)
5. [When to Split](#when-to-split)
6. [When NOT to Split](#when-not-to-split)
7. [Real-World Examples](#real-world-examples)

---

## Definition

### Robert C. Martin's Definition

**"A module should be responsible to one, and only one, actor."**

- **Module**: A class, function, or cohesive set of functions
- **Responsible to**: Would change in response to requests from
- **Actor**: A group of users or stakeholders who would request changes

### Key Insight

SRP is NOT about "doing one thing" (that's a different principle).
SRP is about "having one reason to change" (one actor).

**Example:**
```python
# ✅ CORRECT: Multiple methods, ONE actor (Accounting)
class PayrollCalculator:
    def calculate_gross_pay(self, employee):
        pass

    def calculate_deductions(self, employee):
        pass

    def calculate_net_pay(self, employee):
        pass

    # All methods serve the Accounting department (one actor)
```

---

## Actor-Driven vs Task-Driven

### Task-Driven Approach (WRONG)

**"A class should do one thing"**

```python
# ❌ WRONG: Overly granular (misunderstanding SRP)
class PayCalculator:
    def calculate(self, hours, rate):
        return hours * rate

class DeductionCalculator:
    def calculate(self, gross, rate):
        return gross * rate

class NetPayCalculator:
    def calculate(self, gross, deductions):
        return gross - deductions

# Result: 3 classes for ONE actor (Accounting)
# This is over-engineering, not SRP
```

### Actor-Driven Approach (CORRECT)

**"A class should serve one actor"**

```python
# ✅ CORRECT: One class, one actor (Accounting)
class PayrollCalculator:
    def calculate_gross_pay(self, hours, rate):
        return hours * rate

    def calculate_deductions(self, gross, rate):
        return gross * rate

    def calculate_net_pay(self, gross, deductions):
        return gross - deductions

# All methods serve Accounting department
# Single Responsibility = Single Actor
```

---

## Common Misconceptions

### Misconception 1: "One Method Per Class"

**WRONG:** "SRP means each class has exactly one method"

**CORRECT:** "SRP means each class serves exactly one actor"

```python
# ❌ OVER-ENGINEERED
class AddUser:
    def execute(self, user): pass

class DeleteUser:
    def execute(self, user): pass

class UpdateUser:
    def execute(self, user): pass

# ✅ PROPERLY DESIGNED
class UserRepository:  # Actor: DBA/Data Access
    def add(self, user): pass
    def delete(self, user): pass
    def update(self, user): pass
```

### Misconception 2: "Small Classes Are Always Better"

**WRONG:** "Split every large class into smaller ones"

**CORRECT:** "Split classes that serve multiple actors"

```python
# ✅ GOOD: Large class, single actor (Business Logic)
class OrderProcessor:  # Actor: Sales/Business team
    # 300 lines of code
    # 15 methods
    # All serve Sales actor
    # High cohesion (TCC > 0.5)
    # Single Responsibility ✓

# ❌ BAD: Small class, multiple actors
class User:  # 50 lines
    def calculate_pay(self):    # Actor: Accounting
        pass

    def report_hours(self):     # Actor: HR
        pass

# Violates SRP despite being small!
```

### Misconception 3: "Helper Methods Violate SRP"

**WRONG:** "Private helper methods mean class does too much"

**CORRECT:** "Helper methods are fine if they serve the same actor"

```python
# ✅ GOOD: Helper methods serving same actor
class InvoiceGenerator:  # Actor: Accounting
    def generate(self, order):
        header = self._generate_header(order)
        items = self._generate_items(order)
        total = self._calculate_total(items)
        return self._format_invoice(header, items, total)

    # All private helpers serve Accounting
    def _generate_header(self, order): pass
    def _generate_items(self, order): pass
    def _calculate_total(self, items): pass
    def _format_invoice(self, header, items, total): pass
```

---

## Identifying Actors

### Step 1: List Stakeholders

Ask: **"Who would request changes to this class?"**

**Example: Employee class**
```python
class Employee:
    def calculate_pay(self):        # Who? → Accounting
        pass

    def report_hours(self):         # Who? → HR
        pass

    def save(self):                 # Who? → DBA
        pass

# Actors identified: Accounting, HR, DBA (3 actors!)
# Violation: Multiple actors → Must split
```

### Step 2: Group Methods by Actor

| Method | Actor | Department |
|--------|-------|------------|
| `calculate_pay()` | Accounting | Finance |
| `calculate_overtime()` | Accounting | Finance |
| `report_hours()` | HR | Human Resources |
| `generate_timesheet()` | HR | Human Resources |
| `save()` | DBA | IT/Database |
| `find_by_id()` | DBA | IT/Database |

**Result:** 3 distinct actors → Need 3 classes

### Step 3: Name Classes by Actor

```python
# ✅ REFACTORED: One class per actor
class PayrollCalculator:     # Actor: Accounting
    def calculate_pay(self, employee):
        pass

    def calculate_overtime(self, employee):
        pass

class TimeTracker:            # Actor: HR
    def report_hours(self, employee):
        pass

    def generate_timesheet(self, employee):
        pass

class EmployeeRepository:     # Actor: DBA
    def save(self, employee):
        pass

    def find_by_id(self, id):
        pass
```

---

## When to Split

### Trigger 1: Multiple Actors Detected

**Rule:** If 2+ distinct actors would request changes, split.

```python
# ❌ VIOLATION: 2 actors
class ReportGenerator:
    def generate_pdf(self, data):      # Actor: Business users
        pass

    def send_to_printer(self, pdf):    # Actor: IT/Operations
        pass

# ✅ FIX: Split by actor
class ReportFormatter:                 # Actor: Business users
    def generate_pdf(self, data):
        pass

class PrintService:                    # Actor: IT/Operations
    def send_to_printer(self, pdf):
        pass
```

### Trigger 2: Method Names with "and"

**Rule:** Method doing A "and" B likely serves 2 actors.

```python
# ❌ VIOLATION
def validate_and_save_user(data):
    # Validation (Actor: Business Logic)
    if not data.get("email"):
        raise ValueError("Invalid")

    # Persistence (Actor: DBA)
    db.save(data)

# ✅ FIX
def validate_user(data):      # Actor: Business Logic
    if not data.get("email"):
        return False
    return True

def save_user(data):          # Actor: DBA
    return db.save(data)
```

### Trigger 3: High Constructor Dependencies (>4)

**Rule:** >4 dependencies suggests multiple responsibilities.

```python
# ❌ VIOLATION: 8 dependencies
class UserService:
    def __init__(
        self,
        db_conn,           # DBA actor
        cache,             # Infrastructure actor
        email_service,     # Notification actor
        auth_service,      # Security actor
        logger,            # Monitoring actor
        analytics,         # Analytics actor
        payment_gateway,   # Finance actor
        notification_hub   # Communication actor
    ):
        # 8 actors! → God Class

# ✅ FIX: Split by actor domain
class UserAuthService:            # Actor: Security
    def __init__(self, auth_service, logger):
        pass

class UserNotificationService:    # Actor: Communication
    def __init__(self, email_service, notification_hub):
        pass

class UserAnalyticsService:       # Actor: Analytics
    def __init__(self, analytics, logger):
        pass
```

### Trigger 4: Low Cohesion (TCC <0.33)

**Rule:** Methods don't share instance variables → Low cohesion → Multiple actors

```python
# ❌ VIOLATION: TCC = 0.2 (low cohesion)
class DataProcessor:
    def __init__(self):
        self.cache = Cache()
        self.db = Database()
        self.api_client = APIClient()

    def process_local_data(self):
        # Uses: self.cache
        pass

    def process_remote_data(self):
        # Uses: self.api_client
        pass

    def save_data(self):
        # Uses: self.db
        pass

# Methods share few instance variables → Low cohesion → Multiple actors
```

---

## When NOT to Split

### Case 1: High Cohesion Despite Size

```python
# ✅ DON'T SPLIT: 400 lines, but TCC = 0.8 (high cohesion)
class PayrollCalculator:  # Actor: Accounting
    def __init__(self):
        self.tax_tables = load_tax_tables()
        self.benefit_rates = load_benefit_rates()
        self.overtime_rules = load_overtime_rules()

    # 15 methods, all use same instance variables
    # All serve Accounting department
    # High cohesion = Single Responsibility ✓
```

### Case 2: Private Helpers for Same Actor

```python
# ✅ DON'T SPLIT: Helper methods serve same actor
class InvoiceGenerator:  # Actor: Accounting
    def generate(self, order):
        # Public API
        pass

    # 10 private helper methods
    # All support invoice generation (Accounting actor)
    def _calculate_tax(self): pass
    def _calculate_discount(self): pass
    def _format_currency(self): pass
    # etc.
```

### Case 3: Utility Classes (No Actor)

```python
# ✅ DON'T SPLIT: Pure utility (no actor)
class StringUtils:
    @staticmethod
    def capitalize(s): pass

    @staticmethod
    def trim(s): pass

    @staticmethod
    def is_empty(s): pass

# No actor → No SRP violation
# These are stateless utilities
```

---

## Real-World Examples

### Example 1: E-Commerce Order

**❌ VIOLATION: 4 Actors**

```python
class Order:
    def calculate_total(self):       # Actor: Business Logic
        pass

    def charge_credit_card(self):    # Actor: Payment Processing
        pass

    def send_confirmation_email(self): # Actor: Marketing/Communication
        pass

    def save_to_database(self):      # Actor: DBA
        pass

# 4 actors → Must split
```

**✅ REFACTORED: 4 Classes**

```python
class Order:                          # Actor: Business Logic
    def calculate_total(self):
        pass

class PaymentProcessor:               # Actor: Finance/Payment
    def charge_credit_card(self, order):
        pass

class OrderNotifier:                  # Actor: Marketing
    def send_confirmation(self, order):
        pass

class OrderRepository:                # Actor: DBA
    def save(self, order):
        pass
```

### Example 2: User Authentication

**❌ VIOLATION: 3 Actors**

```python
class AuthService:
    def login(self, credentials):         # Actor: Security
        pass

    def log_login_attempt(self, user):    # Actor: Monitoring
        pass

    def send_2fa_code(self, user):        # Actor: Communication
        pass
```

**✅ REFACTORED: 3 Classes**

```python
class Authenticator:                      # Actor: Security
    def login(self, credentials):
        pass

class AuditLogger:                        # Actor: Monitoring
    def log_login_attempt(self, user):
        pass

class TwoFactorService:                   # Actor: Communication
    def send_code(self, user):
        pass
```

### Example 3: Report Generation (Tricky!)

**✅ CORRECT: Looks like 2 actors, but really 1**

```python
class SalesReport:  # Actor: Business/Sales team
    def gather_data(self):
        # Gather sales data
        pass

    def calculate_metrics(self):
        # Calculate totals, averages, etc.
        pass

    def format_as_pdf(self):
        # Format data into PDF
        pass

# Question: Aren't these 3 actors (data, calculation, formatting)?
# Answer: NO - All serve Sales team actor
# The report is one unit of work for Sales
# High cohesion (all methods share sales data)
# Single Responsibility ✓
```

**When to split:**
```python
# ❌ VIOLATION: Now 2 actors
class SalesReport:
    def gather_data(self):        # Actor: Sales team
        pass

    def calculate_metrics(self):  # Actor: Sales team
        pass

    def format_as_pdf(self):      # Actor: Sales team
        pass

    def email_to_executives(self):  # Actor: IT/Communication team
        pass

# Now we have 2 actors:
# 1. Sales team (report content)
# 2. IT/Communication (delivery mechanism)
# → Must split
```

**✅ REFACTORED:**
```python
class SalesReport:                # Actor: Sales team
    def gather_data(self): pass
    def calculate_metrics(self): pass
    def format_as_pdf(self): pass

class ReportDistributor:          # Actor: IT/Communication
    def email_to_executives(self, report): pass
```

---

## Summary: Actor-Driven SRP

### Quick Checklist

**Ask these questions:**

1. ✅ "How many actors would request changes to this class?"
   - 1 actor → SRP compliant
   - 2+ actors → SRP violation

2. ✅ "Can I group methods by actor/stakeholder?"
   - All methods serve same actor → SRP compliant
   - Methods serve different actors → SRP violation

3. ✅ "Do methods share instance variables?" (Cohesion check)
   - High cohesion (TCC >0.5) → Likely single actor
   - Low cohesion (TCC <0.33) → Likely multiple actors

4. ✅ "Would different teams/departments request changes?"
   - Same team → SRP compliant
   - Different teams → SRP violation

### Key Principles

1. **SRP = One Actor, Not One Method**
   - Multiple methods serving same actor is FINE
   - One method serving multiple actors is VIOLATION

2. **Size ≠ Violation**
   - Large class with high cohesion is FINE
   - Small class with multiple actors is VIOLATION

3. **Helpers Are OK**
   - Private methods supporting same actor are FINE
   - Just ensure they serve the same responsibility

4. **Actor-Driven Refactoring**
   - Split by actor, not by arbitrary size limits
   - Name classes by actor/responsibility

---

**Last Updated:** 2025-11-02
**See Also:**
- [../examples/examples.md](../examples/examples.md) - Real codebase examples with violations and fixes
- [../SKILL.md](../SKILL.md) - Complete SRP validation workflow with detection methods
