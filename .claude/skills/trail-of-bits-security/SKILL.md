---
name: trail-of-bits-security
description: Security audit methodology including static analysis, fuzzing, Semgrep custom rules, property-based testing, and smart contract security.
---

# Trail of Bits Security Methodology

## Overview

Trail of Bits security methodology focuses on systematic code review, automated static analysis, fuzzing, property-based testing, and formal verification to find vulnerabilities at scale.

## Static Analysis with Semgrep

```bash
# Install
pip install semgrep

# Run built-in security rulesets
semgrep --config=p/python-security .
semgrep --config=p/javascript .
semgrep --config=p/golang .
semgrep --config=p/owasp-top-ten .
semgrep --config=p/sql-injection .
semgrep --config=p/jwt .

# Run with output formats
semgrep --config=auto --json --output=results.json .
semgrep --config=auto --sarif --output=results.sarif .
```

```yaml
# custom-rules/security.yaml - Custom Semgrep rules
rules:
  - id: hardcoded-secret
    patterns:
      - pattern: $KEY = "..."
      - metavariable-regex:
          metavariable: $KEY
          regex: '(?i)(password|secret|api_key|token|auth)'
      - metavariable-regex:
          metavariable: "\"...\""
          regex: '[a-zA-Z0-9+/]{20,}'
    message: "Hardcoded secret detected in variable $KEY"
    severity: ERROR
    languages: [python, javascript, typescript]

  - id: sql-injection-format-string
    pattern: |
      $DB.execute(f"... {$VAR} ...")
    message: "Potential SQL injection via f-string formatting"
    severity: ERROR
    languages: [python]
    fix: |
      $DB.execute("... %s ...", ($VAR,))

  - id: pickle-deserialization
    patterns:
      - pattern: pickle.loads($DATA)
    message: "Unsafe deserialization with pickle - use json or msgpack instead"
    severity: ERROR
    languages: [python]

  - id: jwt-none-algorithm
    patterns:
      - pattern: jwt.decode($TOKEN, algorithms=["none"])
      - pattern: jwt.decode($TOKEN, options={"verify_signature": False})
    message: "JWT signature verification disabled"
    severity: ERROR
    languages: [python]

  - id: ssrf-requests
    patterns:
      - pattern: requests.get($URL)
      - pattern: requests.post($URL, ...)
    pattern-not-inside: |
      def $FUNC(...):
        ...
        $URL = "https://..."
        ...
    message: "Potential SSRF - validate URL before making external requests"
    severity: WARNING
    languages: [python]
```

## Python Fuzzing with Atheris

```python
# pip install atheris
import atheris
import sys
import json

# Fuzz a JSON parser or API handler
def TestOneInput(data: bytes):
    fdp = atheris.FuzzedDataProvider(data)

    try:
        # Generate structured fuzz inputs
        user_input = fdp.ConsumeString(100)
        amount = fdp.ConsumeFloat()
        user_id = fdp.ConsumeInt(32)

        # Test your function
        result = process_order(user_id=user_id, amount=amount, note=user_input)

        # Invariant checks (should never raise)
        assert result["total"] >= 0, "Total cannot be negative"
        assert isinstance(result["order_id"], str), "Order ID must be string"

    except (ValueError, KeyError, TypeError):
        # Expected exceptions from bad input
        pass

    # Never allow: unhandled exceptions, crashes, assertion failures

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
```

```python
# Structured fuzzing with Hypothesis
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

# Property-based testing
@given(
    amount=st.floats(min_value=0.01, max_value=1_000_000),
    items=st.lists(
        st.fixed_dictionaries({
            "id": st.integers(min_value=1),
            "qty": st.integers(min_value=1, max_value=100),
            "price": st.floats(min_value=0.01, max_value=10_000),
        }),
        min_size=1,
        max_size=20,
    ),
)
@settings(max_examples=1000, suppress_health_check=[HealthCheck.too_slow])
def test_order_total_invariants(amount, items):
    order = create_order(items=items)

    # Properties that must always hold
    assert order.total >= 0
    assert order.total == sum(i["qty"] * i["price"] for i in items)
    assert len(order.line_items) == len(items)

# Stateful testing (model-based)
class ShoppingCartStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.cart = ShoppingCart()
        self.model = {}  # Expected state

    @initialize(product_id=st.integers(min_value=1, max_value=1000))
    def new_cart(self, product_id):
        self.cart = ShoppingCart()
        self.model = {}

    @rule(
        product_id=st.integers(min_value=1, max_value=1000),
        qty=st.integers(min_value=1, max_value=10),
    )
    def add_item(self, product_id, qty):
        self.cart.add(product_id, qty)
        self.model[product_id] = self.model.get(product_id, 0) + qty

    @rule()
    def check_invariants(self):
        for product_id, expected_qty in self.model.items():
            assert self.cart.get_quantity(product_id) == expected_qty

TestCart = ShoppingCartStateMachine.TestCase
```

## Smart Contract Auditing with Slither

```bash
# Install
pip install slither-analyzer

# Run all detectors
slither contracts/ --json results.json

# Run specific detectors
slither contracts/ --detect reentrancy-eth,reentrancy-no-eth,uninitialized-state
slither contracts/ --detect arbitrary-send,controlled-delegatecall

# Print call graph
slither contracts/ --print call-graph

# Print inheritance graph
slither contracts/ --print inheritance

# Check for access control issues
slither contracts/ --detect suicidal,unprotected-upgrade

# Generate human-readable summary
slither contracts/ --checklist
```

```python
# Slither Python API for programmatic analysis
from slither import Slither

slither = Slither("./contracts/MyContract.sol")

for contract in slither.contracts:
    print(f"\nContract: {contract.name}")

    # Check for dangerous patterns
    for function in contract.functions:
        # Check for reentrancy
        if function.is_reentrant:
            print(f"  WARNING: {function.name} may be reentrant")

        # Check for unchecked external calls
        for node in function.nodes:
            for call in node.external_calls_as_expressions:
                print(f"  External call in {function.name}: {call}")

        # Check modifiers
        if not function.modifiers and function.visibility in ["public", "external"]:
            if "owner" in function.name.lower() or "admin" in function.name.lower():
                print(f"  WARNING: {function.name} has no access control modifier")
```

## Memory Safety with AddressSanitizer / Valgrind

```bash
# Compile with AddressSanitizer
clang -fsanitize=address,undefined -fno-omit-frame-pointer -g program.c -o program
./program  # Will report memory errors

# With GCC
gcc -fsanitize=address,leak,undefined -g program.c -o program

# Valgrind for memory analysis
valgrind --tool=memcheck --leak-check=full --show-leak-kinds=all ./program

# ThreadSanitizer for data races
clang -fsanitize=thread -g program.c -o program
./program
```

## Dependency Auditing

```bash
# Python
pip install safety pip-audit
safety check
pip-audit

# Node.js
npm audit
npm audit --audit-level=high
npx audit-ci --high

# Go
go list -json -m all | nancy sleuth

# Rust
cargo audit
cargo deny check advisories
```

## Threat Modeling (STRIDE)

```python
# Automated STRIDE analysis helper
from dataclasses import dataclass
from enum import Enum

class ThreatCategory(Enum):
    SPOOFING = "Spoofing identity"
    TAMPERING = "Tampering with data"
    REPUDIATION = "Repudiation"
    INFO_DISCLOSURE = "Information disclosure"
    DENIAL_OF_SERVICE = "Denial of service"
    ELEVATION_OF_PRIVILEGE = "Elevation of privilege"

@dataclass
class Threat:
    category: ThreatCategory
    component: str
    description: str
    mitigation: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW

def analyze_api_endpoint(endpoint: dict) -> list[Threat]:
    threats = []

    if not endpoint.get("auth_required"):
        threats.append(Threat(
            category=ThreatCategory.SPOOFING,
            component=endpoint["path"],
            description="Unauthenticated endpoint may allow identity spoofing",
            mitigation="Require JWT authentication with signature verification",
            severity="HIGH",
        ))

    if endpoint.get("accepts_user_input") and not endpoint.get("input_validation"):
        threats.append(Threat(
            category=ThreatCategory.TAMPERING,
            component=endpoint["path"],
            description="Unvalidated user input may allow data tampering or injection",
            mitigation="Implement input validation with Pydantic/Zod schemas",
            severity="CRITICAL",
        ))

    if not endpoint.get("rate_limited"):
        threats.append(Threat(
            category=ThreatCategory.DENIAL_OF_SERVICE,
            component=endpoint["path"],
            description="No rate limiting allows DoS attacks",
            mitigation="Implement rate limiting (e.g., 100 req/min per IP)",
            severity="MEDIUM",
        ))

    return threats
```

## CI/CD Security Pipeline

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Semgrep
        uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/python-security
            p/owasp-top-ten
            p/secrets
          publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}

      - name: Run pip-audit
        run: pip-audit --requirement requirements.txt --format=json --output=pip-audit.json

      - name: Run npm audit
        run: npm audit --audit-level=high --json > npm-audit.json

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif
```

## Key Patterns

- **Defense in depth**: authentication + authorization + input validation + output encoding
- **Fuzz entry points**: all network-facing parsers, file format handlers, and deserialization
- **Property testing** finds edge cases that unit tests miss — run 1000+ examples
- **STRIDE** systematically identifies threats — apply to every new feature
- **Pin dependencies** and audit regularly — supply chain attacks are a major vector
- **Static analysis in CI** catches issues before code review

## Models to Use

- **claude-opus-4-5**: Threat modeling, complex vulnerability analysis, formal verification strategy
- **claude-sonnet-4-5**: Semgrep rule writing, fuzzing harness development, audit report writing
- **claude-haiku-3-5**: Simple dependency checks, known vulnerability lookups
