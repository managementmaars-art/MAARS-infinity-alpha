"""
Example 3: Correct SRP Implementation
Classes with single actor despite multiple methods
"""

# ✅ CORRECT: Multiple methods, ONE actor (Accounting)
class PayrollCalculator:
    """Actor: Accounting department

    All methods serve the Accounting department, so this is SRP-compliant
    despite having multiple methods.
    """
    def __init__(self):
        self.tax_tables = load_tax_tables()
        self.benefit_rates = load_benefit_rates()
        self.overtime_rules = load_overtime_rules()

    def calculate_gross_pay(self, employee):
        hours = employee.hours_worked
        rate = employee.hourly_rate
        return hours * rate

    def calculate_deductions(self, employee):
        gross = self.calculate_gross_pay(employee)
        tax_rate = self.tax_tables.get_rate(employee)
        return gross * tax_rate

    def calculate_net_pay(self, employee):
        gross = self.calculate_gross_pay(employee)
        deductions = self.calculate_deductions(employee)
        return gross - deductions

    def calculate_overtime(self, employee):
        overtime_hours = max(0, employee.hours_worked - 40)
        return overtime_hours * employee.hourly_rate * 1.5


# ✅ CORRECT: Large class with high cohesion
class InvoiceGenerator:
    """Actor: Accounting department

    Despite having many methods, all serve the same actor (Accounting)
    and all share instance variables (high cohesion).
    """
    def __init__(self, order):
        self.order = order
        self.tax_rate = 0.08
        self.discount_rate = 0.10

    def generate(self):
        """Public API for invoice generation"""
        header = self._generate_header()
        items = self._generate_items()
        total = self._calculate_total(items)
        return self._format_invoice(header, items, total)

    # Private helper methods - all serve Accounting actor
    def _generate_header(self):
        return {
            'customer': self.order.customer,
            'date': self.order.date,
            'invoice_number': self.order.id
        }

    def _generate_items(self):
        return [
            {
                'name': item.name,
                'quantity': item.quantity,
                'price': item.price
            }
            for item in self.order.items
        ]

    def _calculate_total(self, items):
        subtotal = sum(item['quantity'] * item['price'] for item in items)
        discount = subtotal * self.discount_rate
        tax = (subtotal - discount) * self.tax_rate
        return subtotal - discount + tax

    def _format_invoice(self, header, items, total):
        return {
            'header': header,
            'items': items,
            'total': total
        }
