# Quality Metrics Guide

Comprehensive guide for measuring software quality across multiple dimensions.

## Table of Contents
- [Code Quality Metrics](#code-quality-metrics)
- [Documentation Metrics](#documentation-metrics)
- [Testing Metrics](#testing-metrics)
- [Maintenance Health Metrics](#maintenance-health-metrics)
- [Security Metrics](#security-metrics)
- [Performance Indicators](#performance-indicators)

## Code Quality Metrics

### Lines of Code (LOC)

**What it measures:** Size and complexity indicator

**How to measure:**
```bash
# Total lines
find . -name "*.py" | xargs wc -l

# By component
wc -l src/core/*.py
wc -l src/services/*.py
```

**Using Copilot tools:**
```
grep_search for file extensions
read_file to count lines
```

**Interpretation:**
- 1-1,000 LOC: Small project/library
- 1,000-10,000: Medium project
- 10,000-100,000: Large project
- 100,000+: Very large/enterprise project

**Red flags:**
- Single file >1,000 lines
- Single function >100 lines

### Code Complexity Indicators

**What to look for:**

1. **Deep nesting** (>4 levels):
```python
# Bad - hard to understand
def process(data):
    if data:
        for item in data:
            if item.valid:
                if item.type == 'A':
                    if item.status == 'active':
                        # deeply nested code
```

2. **Long functions** (>50 lines):
```python
def giant_function():
    # 200 lines of code
    # doing many different things
```

3. **Many parameters** (>5):
```python
def complex_func(a, b, c, d, e, f, g, h):
    pass
```

**How to find:**
```
grep_search for "def |function " (with high line counts)
semantic_search for "complex function" or "refactor"
```

**Scoring:**
- Excellent: Functions <30 lines, nesting <3, params <4
- Good: Functions <50 lines, nesting <4, params <5
- Fair: Functions <100 lines, nesting <5, params <6
- Poor: Exceeds fair thresholds

### Code Duplication

**What it measures:** Maintainability and DRY principle

**How to detect:**
- Look for similar function names: `parse_json_1`, `parse_json_2`
- Search for repeated code patterns
- Check for copy-paste comments

**Using tools:**
```
semantic_search for "TODO: remove duplication"
grep_search for similar function signatures
```

**Interpretation:**
- <5% duplication: Excellent
- 5-10%: Good
- 10-20%: Fair
- >20%: Poor

### Naming Conventions

**What to check:**
- Consistent style (snake_case, camelCase, PascalCase)
- Descriptive names (not `x`, `temp`, `data`)
- Standard patterns followed

**Red flags:**
```python
# Poor naming
def fn(x, y):
    temp = x + y
    data = process(temp)
    return data

# Good naming
def calculate_total_price(base_price, tax_rate):
    subtotal = base_price + tax_rate
    final_price = apply_discount(subtotal)
    return final_price
```

### Comments and Documentation

**In-code documentation ratio:**
- Count docstrings, comments
- Compare to total lines

**Quality indicators:**
```python
# Good - explains WHY
# Using exponential backoff to handle rate limiting
retry_with_backoff()

# Bad - explains WHAT (obvious)
# Add 1 to counter
counter += 1
```

**Using tools:**
```
grep_search for "# |""" |///" (comments)
Calculate comment_lines / total_lines
```

**Targets:**
- 10-20% comment ratio: Good balance
- <5%: Under-documented
- >30%: Possibly over-documented or complex code

## Documentation Metrics

### README Quality Checklist

**Essential sections:**
- [ ] Project description (what it does)
- [ ] Installation instructions
- [ ] Basic usage example
- [ ] Requirements/dependencies
- [ ] License information

**Advanced sections:**
- [ ] Architecture overview
- [ ] API documentation
- [ ] Contributing guidelines
- [ ] Troubleshooting
- [ ] Examples gallery
- [ ] FAQ

**Scoring:**
- 5/5 essential + 4+ advanced = ⭐⭐⭐⭐⭐
- 5/5 essential + 2-3 advanced = ⭐⭐⭐⭐
- 4-5/5 essential + 0-1 advanced = ⭐⭐⭐
- 3/5 essential = ⭐⭐
- <3/5 essential = ⭐

### API Documentation Coverage

**For each public function/class:**
- [ ] Description of purpose
- [ ] Parameter types and descriptions
- [ ] Return value type and description
- [ ] Example usage
- [ ] Error conditions

**How to measure:**
```python
# Well-documented
def process_payment(amount: float, currency: str) -> PaymentResult:
    """
    Process a payment transaction.
    
    Args:
        amount: Payment amount in specified currency
        currency: ISO 4217 currency code (e.g., 'USD', 'EUR')
    
    Returns:
        PaymentResult containing transaction_id and status
    
    Raises:
        ValueError: If amount is negative or currency is invalid
        PaymentError: If payment processing fails
    
    Example:
        >>> result = process_payment(100.00, 'USD')
        >>> print(result.transaction_id)
        'tx_123456'
    """
```

**Coverage calculation:**
```
documented_functions / total_public_functions × 100%
```

**Scoring:**
- 90-100% coverage: ⭐⭐⭐⭐⭐
- 70-89% coverage: ⭐⭐⭐⭐
- 50-69% coverage: ⭐⭐⭐
- 30-49% coverage: ⭐⭐
- <30% coverage: ⭐

### User Guide Quality

**What to assess:**
- Getting started tutorial
- Step-by-step examples
- Common use cases covered
- Troubleshooting guide
- Visual aids (diagrams, screenshots)

**Using tools:**
```
file_search for "docs/*.md" or "*.rst"
read_file to assess content quality
```

### Changelog Presence

**Good changelog example:**
```markdown
## [1.2.0] - 2025-01-10

### Added
- New export feature for PDF reports
- Support for custom themes

### Changed
- Improved error messages
- Updated dependencies

### Fixed
- Bug in date parsing
- Memory leak in cache
```

**Scoring:**
- Detailed changelog with semantic versioning: ⭐⭐⭐⭐⭐
- Basic changelog: ⭐⭐⭐
- Only git commits: ⭐
- No changelog: No stars

## Testing Metrics

### Test Presence by Type

**Test types to look for:**

1. **Unit tests**
```python
def test_calculate_total():
    assert calculate_total(10, 2) == 20
```

2. **Integration tests**
```python
def test_api_endpoint():
    response = client.post('/api/users', data={'name': 'Test'})
    assert response.status_code == 201
```

3. **End-to-end tests**
```python
def test_user_workflow():
    # Complete user journey
    signup()
    login()
    create_post()
    logout()
```

**How to measure:**
```
file_search for "test_*.py" or "*.test.js"
grep_search for "def test_" or "it("
Count by type based on naming/location
```

**Scoring:**
- All three types present: ⭐⭐⭐⭐⭐
- Unit + integration: ⭐⭐⭐⭐
- Only unit tests: ⭐⭐⭐
- Few/no tests: ⭐ or no stars

### Test Coverage

**Where to find:**
- `.coverage` files
- Coverage reports in CI logs
- Badges in README
- `coverage.xml` or `coverage.json`

**Read from config:**
```python
# pytest.ini or .coveragerc
[coverage:run]
omit = tests/*

# package.json
"jest": {
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80
    }
  }
}
```

**Interpretation:**
- 80-100%: ⭐⭐⭐⭐⭐
- 60-79%: ⭐⭐⭐⭐
- 40-59%: ⭐⭐⭐
- 20-39%: ⭐⭐
- <20%: ⭐

### Test Quality Indicators

**Good test characteristics:**

1. **Clear naming**
```python
# Good
def test_user_cannot_delete_others_posts():
    pass

# Bad
def test_1():
    pass
```

2. **Arrange-Act-Assert pattern**
```python
def test_add_item_to_cart():
    # Arrange
    cart = ShoppingCart()
    item = Item("Widget", 10.00)
    
    # Act
    cart.add_item(item)
    
    # Assert
    assert cart.total() == 10.00
    assert len(cart.items) == 1
```

3. **Mocking external dependencies**
```python
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {'data': 'test'}
    result = fetch_data()
    assert result == {'data': 'test'}
```

**Red flags:**
- Tests that depend on external services
- Tests without assertions
- Flaky tests (random failures)
- Tests that test implementation, not behavior

### CI/CD Integration

**What to check:**
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
      - name: Upload coverage
        run: codecov
```

**Scoring:**
- Tests run on every PR + coverage reporting: ⭐⭐⭐⭐⭐
- Tests run on every PR: ⭐⭐⭐⭐
- Tests run on push to main: ⭐⭐⭐
- Manual testing only: ⭐

## Maintenance Health Metrics

### Commit Activity

**What to measure:**
- Commits in last 30 days
- Commits in last 90 days
- Commits in last year

**Using Git:**
```bash
git log --since="30 days ago" --oneline | wc -l
```

**Interpretation:**
- Active (weekly commits): Healthy
- Moderate (monthly commits): Stable
- Inactive (no commits in 6+ months): Potentially abandoned

### Issue Tracker Health

**Metrics to collect:**

1. **Open vs Closed ratio**
```
health_score = closed_issues / (open_issues + closed_issues)
```

2. **Response time**
- Time from issue creation to first response
- Average: calculated from sample

3. **Resolution time**
- Time from issue creation to closure
- Average: calculated from sample

**Scoring:**
- Response <24h, most issues closed: ⭐⭐⭐⭐⭐
- Response <1 week, regular closures: ⭐⭐⭐⭐
- Response <1 month, some closures: ⭐⭐⭐
- Slow responses, many stale issues: ⭐⭐
- No issue management: ⭐

### Dependency Health

**What to check:**

1. **Outdated dependencies**
```json
// package.json
{
  "dependencies": {
    "express": "^4.17.1",  // Check if latest is 5.x
    "lodash": "^4.17.20"   // Check for security issues
  }
}
```

2. **Security vulnerabilities**
- Look for `npm audit` results
- Check for `pip-audit` or `safety` reports
- Review dependabot PRs

3. **Dependency count**
- Too many dependencies = higher risk
- Look for "dependency bloat"

**Using tools:**
```
read_file package.json or requirements.txt
Count dependencies
Check for security badges in README
```

**Red flags:**
- Dependencies with known CVEs
- Unmaintained dependencies (no updates in years)
- Excessive transitive dependencies

### Release Cadence

**What to measure:**
- Time between releases
- Semantic versioning adherence
- Release notes quality

**Healthy patterns:**
- Major releases: yearly
- Minor releases: quarterly
- Patch releases: as needed (bugs/security)

**Finding releases:**
```
file_search for CHANGELOG or RELEASES
Check git tags: git tag -l
Look for GitHub releases
```

## Security Metrics

### Security Best Practices Checklist

**Code level:**
- [ ] No hardcoded secrets (API keys, passwords)
- [ ] Input validation present
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output escaping)
- [ ] CSRF protection

**How to check:**
```
grep_search for "password.*=.*'" (hardcoded passwords)
grep_search for "api_key.*=.*'" (hardcoded API keys)
semantic_search for "security vulnerability"
```

**Dependencies:**
- [ ] Regular security updates
- [ ] Vulnerability scanning (dependabot, snyk)
- [ ] No dependencies with known CVEs

**Configuration:**
- [ ] Secrets management (env vars, vault)
- [ ] Secure defaults
- [ ] Security headers configured

**Scoring:**
- All critical checks pass: ⭐⭐⭐⭐⭐
- Most checks pass, minor issues: ⭐⭐⭐⭐
- Some security practices: ⭐⭐⭐
- Obvious vulnerabilities: ⭐ or ⭐⭐
- Critical security issues: No stars + urgent flag

### Authentication & Authorization

**What to verify:**
- Authentication mechanism present
- Password hashing (bcrypt, argon2)
- Token-based auth (JWT, OAuth)
- Authorization checks in place
- Session management

**Finding evidence:**
```
semantic_search for "authentication" or "login"
grep_search for "bcrypt|jwt|oauth"
Read auth middleware code
```

## Performance Indicators

**Note:** Cannot measure runtime performance without execution, but can identify potential issues.

### Performance Code Patterns

**Good patterns:**
```python
# Efficient
users = User.objects.select_related('profile').all()  # Single query

# Database indexing
class User(Model):
    email = CharField(max_length=255, db_index=True)
```

**Bad patterns:**
```python
# N+1 query problem
for user in users:
    print(user.profile)  # Separate query per user

# Loading all data
all_records = Table.objects.all()  # Could be millions
```

**How to detect:**
```
grep_search for ".all()" or "SELECT *"
semantic_search for "performance optimization"
Look for pagination implementation
```

### Caching Strategy

**What to look for:**
```python
# Redis caching
@cache.cached(timeout=300)
def expensive_operation():
    pass

# Memoization
@lru_cache(maxsize=100)
def fibonacci(n):
    pass
```

**Detection:**
```
grep_search for "cache|memoize"
Check for Redis, Memcached config
```

### Async/Concurrent Patterns

**Modern async code:**
```python
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
```

**Detection:**
```
grep_search for "async def|await"
Look for threading, multiprocessing
Check for job queue (Celery, RQ)
```

## Composite Quality Score

### Weighted Scoring Formula

```
Overall Score = (
    Documentation × 0.25 +
    Testing × 0.30 +
    Code Quality × 0.20 +
    Maintenance × 0.15 +
    Security × 0.10
)
```

### Score Interpretation

**5.0 stars:** Production-ready, excellent quality
- Comprehensive docs with examples
- >80% test coverage with CI/CD
- Clean, well-structured code
- Active maintenance
- Security best practices

**4.0 stars:** High quality, minor improvements needed
- Good documentation
- >60% test coverage
- Generally clean code
- Regular updates
- Basic security measures

**3.0 stars:** Adequate, functional with issues
- Basic documentation
- Some tests present
- Acceptable code quality
- Sporadic updates
- Some security concerns

**2.0 stars:** Below standard, needs work
- Minimal documentation
- Few tests
- Code quality issues
- Infrequent updates
- Security gaps

**1.0 stars:** Poor quality, major issues
- Little/no documentation
- No tests
- Poor code quality
- Unmaintained
- Security vulnerabilities

## Measurement Workflow

### Step-by-Step Process

1. **Initialize metrics template:**
```markdown
## Quality Metrics: [Tool Name]

### Code Quality: [Score]/5
- LOC: 
- Complexity: 
- Duplication: 

### Documentation: [Score]/5
- README: 
- API docs: 
- User guide: 

### Testing: [Score]/5
- Test types: 
- Coverage: 
- CI/CD: 

### Maintenance: [Score]/5
- Activity: 
- Issues: 
- Dependencies: 

### Security: [Score]/5
- Best practices: 
- Auth: 
- Vulnerabilities: 

### Overall: [Score]/5
```

2. **Gather data systematically:**
- Use file_search for test files, docs
- Use grep_search for patterns
- Use read_file for details
- Calculate ratios

3. **Score each dimension:**
- Apply scoring rubrics from this guide
- Document evidence for each score
- Note specific findings

4. **Calculate composite score:**
- Apply weighted formula
- Round to nearest 0.5
- Provide score summary

5. **Add recommendations:**
- Identify top 3 improvements
- Provide specific, actionable suggestions
- Prioritize by impact

## Limitations and Caveats

- **Static analysis only:** Cannot measure runtime performance
- **Snapshot in time:** Metrics reflect current state only
- **Context matters:** Small tools may naturally have different metrics
- **Subjective elements:** Some quality aspects require judgment
- **Tool dependency:** Relies on available Copilot tools for measurement
