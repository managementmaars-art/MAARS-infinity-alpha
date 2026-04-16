"""
Example 1: Naming Pattern Violations
Methods with "and" in name indicate SRP violations (40% confidence)
"""

# ❌ VIOLATION: Method name contains "and"
def validate_and_save_user(data):
    """Violates SRP - serves 2 actors"""
    # Validation logic (Actor 1: Validation team)
    if not data.get("email"):
        raise ValueError("Invalid email")

    # Persistence logic (Actor 2: DBA team)
    db.save(data)


# ✅ FIX: Split by actor
def validate_user(data):
    """Actor: Validation team"""
    if not data.get("email"):
        raise ValueError("Invalid email")
    return True


def save_user(data):
    """Actor: DBA team"""
    return db.save(data)


# ❌ VIOLATION: Multiple actors in class
class Employee:
    def calculate_pay(self):
        """Actor: Accounting"""
        pass

    def report_hours(self):
        """Actor: HR"""
        pass

    def save(self):
        """Actor: DBA"""
        pass


# ✅ CORRECT: One actor per class
class PayCalculator:
    """Actor: Accounting"""
    def calculate(self, employee):
        pass


class HourReporter:
    """Actor: HR"""
    def report(self, employee):
        pass


class EmployeeRepository:
    """Actor: DBA"""
    def save(self, employee):
        pass
