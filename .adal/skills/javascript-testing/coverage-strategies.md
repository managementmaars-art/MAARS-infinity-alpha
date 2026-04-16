## Coverage Strategies

Guide for achieving 100% test coverage without cheating.

### Coverage Means

- **Statements**: 100% - Every statement executed
- **Branches**: 100% - Every if/else tested
- **Functions**: 100% - Every function called
- **Lines**: 100% - Every line executed

**No exceptions. No coverage ignore comments.**

### Strategy 1: Refactor I/O-Heavy Code

Separate business logic from I/O operations.

**Before - Untestable:**

```javascript
function main() {
  process.stdin.on('data', (chunk) => {
    const input = JSON.parse(chunk);
    const result = complexProcessing(input);
    writeToFile(formatOutput(result));
  });
}
```

**After - Testable:**

```javascript
// Export testable logic
export function parseInput(chunk) {
  return JSON.parse(chunk);
}

export function processData(input) {
  return complexProcessing(input);
}

export function formatOutput(result) {
  return format(result);
}

// Thin I/O wrapper
function main() {
  process.stdin.on('data', (chunk) => {
    const input = parseInput(chunk);
    const result = processData(input);
    const formatted = formatOutput(result);
    saveOutput(formatted);
  });
}
```

### Strategy 2: Test Error Paths

Every try-catch needs both success and error tests.

```javascript
export function readConfig(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    throw new Error(`Invalid config: ${filePath}`);
  }
}

// Tests
test('success', () => {
  vi.spyOn(fs, 'readFileSync').mockReturnValue('{"key":"value"}');
  expect(readConfig('config.json')).toEqual({ key: 'value' });
});

test('file not found', () => {
  vi.spyOn(fs, 'readFileSync').mockImplementation(() => {
    throw new Error('ENOENT');
  });
  expect(() => readConfig('missing.json')).toThrow('Invalid config');
});

test('invalid JSON', () => {
  vi.spyOn(fs, 'readFileSync').mockReturnValue('not json');
  expect(() => readConfig('config.json')).toThrow('Invalid config');
});
```

### Strategy 3: Test All Branches

Every conditional creates branches.

```javascript
export function classifyValue(value) {
  if (value === null || value === undefined) return 'null-ish'; // 1
  if (typeof value !== 'number') return 'non-number'; // 2
  if (value < 0) return 'negative'; // 3
  if (value === 0) return 'zero'; // 4
  if (value < 10) return 'small'; // 5
  return 'large'; // 6
}

// Test ALL 6 branches
test('null-ish', () => {
  expect(classifyValue(null)).toBe('null-ish');
  expect(classifyValue(undefined)).toBe('null-ish');
});
test('non-number', () => expect(classifyValue('x')).toBe('non-number'));
test('negative', () => expect(classifyValue(-1)).toBe('negative'));
test('zero', () => expect(classifyValue(0)).toBe('zero'));
test('small', () => expect(classifyValue(5)).toBe('small'));
test('large', () => expect(classifyValue(20)).toBe('large'));
```

### Strategy 4: Test Logical Operators

Logical operators (&&, ||) create branches.

```javascript
export function isValid(value) {
  return value && value.length > 0;
}

// All branches
test('valid non-empty', () => expect(isValid('test')).toBe(true));
test('valid empty', () => expect(isValid('')).toBe(false));
test('null/undefined', () => {
  expect(isValid(null)).toBe(false);
  expect(isValid(undefined)).toBe(false);
});
```

### Strategy 5: Mock process.exit()

```javascript
export function main(args) {
  if (args.length === 0) {
    console.error('Usage: script.js <file>');
    process.exit(1);
  }
  if (!fs.existsSync(args[0])) {
    console.error('File not found');
    process.exit(1);
  }
  processFile(args[0]);
  process.exit(0);
}

// Tests
let mockExit;
beforeEach(
  () => (mockExit = vi.spyOn(process, 'exit').mockImplementation(() => {}))
);
afterEach(() => mockExit.mockRestore());

test('no args', () => {
  main([]);
  expect(mockExit).toHaveBeenCalledWith(1);
});

test('file not found', () => {
  vi.spyOn(fs, 'existsSync').mockReturnValue(false);
  main(['missing.txt']);
  expect(mockExit).toHaveBeenCalledWith(1);
});

test('success', () => {
  vi.spyOn(fs, 'existsSync').mockReturnValue(true);
  vi.spyOn(global, 'processFile').mockImplementation(() => {});
  main(['file.txt']);
  expect(mockExit).toHaveBeenCalledWith(0);
});
```

### Strategy 6: Test Switch Statements

Every case including default must be tested.

```javascript
export function getStatus(code) {
  switch (code) {
    case 200:
      return 'success';
    case 404:
      return 'not found';
    case 500:
      return 'server error';
    default:
      return 'unknown';
  }
}

test('200', () => expect(getStatus(200)).toBe('success'));
test('404', () => expect(getStatus(404)).toBe('not found'));
test('500', () => expect(getStatus(500)).toBe('server error'));
test('other', () => expect(getStatus(999)).toBe('unknown'));
```

### Strategy 7: Test Ternary Operators

```javascript
export function getLabel(value) {
  return value ? 'yes' : 'no';
}

test('truthy', () => expect(getLabel('x')).toBe('yes'));
test('falsy', () => expect(getLabel('')).toBe('no'));
```

### Strategy 8: Test Early Returns

```javascript
export function validate(data) {
  if (!data) return { valid: false, error: 'Missing data' };
  if (!data.email) return { valid: false, error: 'Missing email' };
  if (!data.email.includes('@'))
    return { valid: false, error: 'Invalid email' };
  return { valid: true };
}

test('missing data', () => {
  expect(validate(null).error).toBe('Missing data');
});
test('missing email', () => {
  expect(validate({}).error).toBe('Missing email');
});
test('invalid email', () => {
  expect(validate({ email: 'x' }).error).toBe('Invalid email');
});
test('valid', () => {
  expect(validate({ email: 'a@b.c' }).valid).toBe(true);
});
```

### Strategy 9: Test Async Error Handling

```javascript
export async function fetchUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error('User not found');
    return await response.json();
  } catch (error) {
    console.error('Failed:', error);
    throw error;
  }
}

test('success', async () => {
  global.fetch = vi.fn(() =>
    Promise.resolve({ ok: true, json: async () => ({ id: 1 }) })
  );
  expect(await fetchUser(1)).toEqual({ id: 1 });
});

test('404', async () => {
  global.fetch = vi.fn(() => Promise.resolve({ ok: false }));
  await expect(fetchUser(1)).rejects.toThrow('User not found');
});

test('network error', async () => {
  global.fetch = vi.fn(() => Promise.reject(new Error('Network')));
  await expect(fetchUser(1)).rejects.toThrow('Network');
});
```

### Strategy 10: Test Optional Chaining

```javascript
export function getEmail(user) {
  return user?.email || 'no-email';
}

test('with email', () => {
  expect(getEmail({ email: 'a@b.c' })).toBe('a@b.c');
});
test('without email', () => expect(getEmail({})).toBe('no-email'));
test('null user', () => expect(getEmail(null)).toBe('no-email'));
```

### Common Coverage Gaps

**Gap 1: Forgot else**

```javascript
export function check(value) {
  if (value > 0) return 'positive';
  // Missing test for value <= 0
}
```

**Gap 2: Forgot error path**

```javascript
export function parse(json) {
  try {
    return JSON.parse(json);
  } catch (error) {
    return null; // Missing test
  }
}
```

**Gap 3: Forgot default case**

```javascript
export function handle(type) {
  switch (type) {
    case 'A':
      return 'a';
    default:
      return 'unknown'; // Missing test
  }
}
```

**Gap 4: Forgot second condition**

```javascript
export function validate(a, b) {
  if (a && b) return true;
  return false;
  // Need tests for: a=T,b=F and a=F,b=T
}
```

### Checking Coverage

```bash
pnpm test:coverage
# Must show 100% for all metrics
```

If not 100%:

1. Open `coverage/index.html`
2. Find uncovered lines (red)
3. Identify missing branch/path
4. Write test for that case
5. Re-run coverage

### Refactoring Checklist

When code seems untestable:

- [ ] Separate I/O from business logic
- [ ] Extract pure functions
- [ ] Make dependencies injectable
- [ ] Avoid global state
- [ ] Export internal functions
- [ ] Break down large functions

### 100% Coverage Without Cheating

**Never use:**

- `/* istanbul ignore next */`
- `/* c8 ignore next */`
- `/* c8 ignore start */` ... `/* c8 ignore stop */`

**Instead:**

1. Refactor code to be testable
2. Mock external dependencies
3. Test all branches explicitly
4. Use integration tests for I/O

### Complete Example

```javascript
// hook-processor.js
export function processHookData(data) {
  if (!data) throw new Error('Data required');
  if (!data.tool) throw new Error('Tool required');
  return { tool: data.tool, timestamp: Date.now(), processed: true };
}

export function saveToLog(data) {
  fs.appendFileSync('log.json', JSON.stringify(data) + '\n');
}

function main() {
  process.stdin.on('data', (chunk) => {
    try {
      const input = JSON.parse(chunk.toString());
      const processed = processHookData(input);
      saveToLog(processed);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });
}
```

**Tests - 100% coverage:**

```javascript
describe('processHookData', () => {
  test('valid', () => {
    const result = processHookData({ tool: 'Read' });
    expect(result.tool).toBe('Read');
    expect(result.processed).toBe(true);
  });
  test('no data', () => {
    expect(() => processHookData(null)).toThrow('Data required');
  });
  test('no tool', () => {
    expect(() => processHookData({})).toThrow('Tool required');
  });
});

describe('saveToLog', () => {
  afterEach(() => vi.restoreAllMocks());

  test('appends to log', () => {
    const spy = vi.spyOn(fs, 'appendFileSync').mockImplementation(() => {});
    saveToLog({ tool: 'Read', timestamp: 12345 });
    expect(spy).toHaveBeenCalled();
  });
});
```

Result: **100% statements, branches, functions, lines**.
