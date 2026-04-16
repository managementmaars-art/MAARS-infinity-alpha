## Mocking with Vitest

Complete guide for mocking patterns with Vitest.

### Basic Mocking

```javascript
import { vi } from 'vitest';

const mockFn = vi.fn();
mockFn.mockReturnValue(42);
mockFn.mockImplementation((x) => x * 2);
mockFn.mockResolvedValue({ data: 'test' });
mockFn.mockRejectedValue(new Error('Failed'));
```

### Module Mocking

```javascript
import { vi } from 'vitest';

// Mock entire module
vi.mock('child_process', () => ({
  execSync: vi.fn(() => 'mocked output'),
}));

const { execSync } = await import('child_process');

test('uses mocked execSync', () => {
  expect(execSync('command')).toBe('mocked output');
});
```

### Partial Module Mocking

```javascript
// Mock only specific exports
vi.mock('fs', async () => {
  const actual = await vi.importActual('fs');
  return {
    ...actual,
    readFileSync: vi.fn(() => 'mocked'),
  };
});
```

### Mocking fs Operations

```javascript
import { vi } from 'vitest';
import fs from 'fs';

describe('file operations', () => {
  afterEach(() => vi.restoreAllMocks());

  test('reads file', () => {
    vi.spyOn(fs, 'readFileSync').mockReturnValue('mocked');
    vi.spyOn(fs, 'existsSync').mockReturnValue(true);
    expect(fs.readFileSync('file.txt')).toBe('mocked');
  });

  test('handles errors', () => {
    vi.spyOn(fs, 'readFileSync').mockImplementation(() => {
      throw new Error('ENOENT');
    });
    expect(() => readFile('missing.txt')).toThrow('ENOENT');
  });
});
```

### Mocking process.exit()

```javascript
describe('CLI', () => {
  let mockExit;

  beforeEach(() => {
    mockExit = vi.spyOn(process, 'exit').mockImplementation(() => {});
  });

  afterEach(() => mockExit.mockRestore());

  test('exits with code 1 on error', () => {
    runCLI(['invalid']);
    expect(mockExit).toHaveBeenCalledWith(1);
  });
});
```

### Mocking process.argv

```javascript
describe('argument parsing', () => {
  let originalArgv;

  beforeEach(() => (originalArgv = process.argv));
  afterEach(() => (process.argv = originalArgv));

  test('parses arguments', () => {
    process.argv = ['node', 'script.js', '--verbose', 'input.txt'];
    const args = parseArgs();
    expect(args.verbose).toBe(true);
  });
});
```

### Mocking Environment Variables

```javascript
describe('environment config', () => {
  let originalEnv;

  beforeEach(() => (originalEnv = { ...process.env }));
  afterEach(() => (process.env = originalEnv));

  test('uses env variable', () => {
    process.env.API_KEY = 'test-key';
    expect(loadConfig().apiKey).toBe('test-key');
  });

  test('throws when missing', () => {
    delete process.env.API_KEY;
    expect(() => loadConfig()).toThrow('API_KEY is required');
  });
});
```

### Mocking Timers

```javascript
describe('time-dependent', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  test('calls callback after delay', () => {
    const callback = vi.fn();
    setTimeout(callback, 1000);

    expect(callback).not.toHaveBeenCalled();
    vi.advanceTimersByTime(1000);
    expect(callback).toHaveBeenCalledOnce();
  });

  test('interval multiple times', () => {
    const callback = vi.fn();
    setInterval(callback, 100);
    vi.advanceTimersByTime(350);
    expect(callback).toHaveBeenCalledTimes(3);
  });
});
```

### Mocking Date

```javascript
describe('date-dependent', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  test('formats current date', () => {
    vi.setSystemTime(new Date('2024-01-15T10:00:00Z'));
    expect(formatCurrentDate()).toBe('2024-01-15');
  });

  test('checks expiration', () => {
    vi.setSystemTime(new Date('2024-01-15'));
    const token = { expiresAt: new Date('2024-01-10') };
    expect(isExpired(token)).toBe(true);
  });
});
```

### Mocking fetch/HTTP

```javascript
describe('API calls', () => {
  beforeEach(() => (global.fetch = vi.fn()));
  afterEach(() => vi.restoreAllMocks());

  test('fetches user data', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, name: 'John' }),
    });

    const user = await fetchUser(1);
    expect(user).toEqual({ id: 1, name: 'John' });
  });

  test('handles network error', async () => {
    global.fetch.mockRejectedValue(new Error('Network error'));
    await expect(fetchUser(1)).rejects.toThrow('Network error');
  });

  test('handles HTTP error', async () => {
    global.fetch.mockResolvedValue({ ok: false, status: 404 });
    await expect(fetchUser(1)).rejects.toThrow('User not found');
  });
});
```

### Spy vs Mock vs Stub

**Spy:** Watch real function

```javascript
const spy = vi.spyOn(obj, 'method');
obj.method(); // Calls real implementation
expect(spy).toHaveBeenCalled();
```

**Mock:** Replace implementation

```javascript
const mock = vi.spyOn(obj, 'method').mockReturnValue('mocked');
obj.method(); // Returns 'mocked'
```

**Stub:** Mock with no implementation

```javascript
const stub = vi.fn();
stub(); // Returns undefined
```

### Mock Assertions

```javascript
const mockFn = vi.fn();

expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(3);
expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
expect(mockFn).toHaveBeenLastCalledWith('lastArg');
expect(mockFn).toHaveBeenNthCalledWith(2, 'secondCall');
```

### Cleaning Up Mocks

```javascript
describe('suite', () => {
  afterEach(() => {
    vi.restoreAllMocks(); // Restore original implementations
    vi.clearAllMocks(); // Clear call history
    vi.resetAllMocks(); // Clear history + reset implementations
  });
});
```

**Differences:**

- `restoreAllMocks()`: Restores originals
- `clearAllMocks()`: Clears history, keeps mocks
- `resetAllMocks()`: Clears history + resets

### When to Mock vs Real

**Mock:**

- External APIs (HTTP, database)
- Slow/destructive fs operations
- process.exit() (prevents termination)
- Date.now(), timers (deterministic)
- External services (email, payments)
- Random generation (reproducible)

**Use Real:**

- Pure JS libraries (lodash, date-fns)
- JSDOM for HTML parsing
- Internal modules/utilities
- Data transformations
- Simple helpers

### Best Practices

1. **Keep mocks simple** - No complex implementations
2. **Mock at boundaries** - External deps, not internal logic
3. **Clean up** - Always restore in afterEach
4. **Avoid over-mocking** - Too many = testing mocks, not code
5. **Use spies when possible** - Spy on real over replacing
6. **Document why** - Comment why mocked

### Common Mistakes

❌ **Don't mock everything**

```javascript
vi.mock('./helper1');
vi.mock('./helper2');
vi.mock('./helper3');
// Now testing mocks, not real code
```

❌ **Don't mock implementation details**

```javascript
const spy = vi.spyOn(obj, '_privateMethod');
obj.publicMethod();
expect(spy).toHaveBeenCalled(); // Brittle!
```

❌ **Don't forget to restore**

```javascript
test('with mock', () => {
  vi.spyOn(fs, 'readFileSync').mockReturnValue('test');
  // Forgot restore - next test uses mock
});
```

✅ **Do mock externals**

```javascript
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: async () => ({ data: 'test' }),
});
```

✅ **Do restore in afterEach**

```javascript
afterEach(() => vi.restoreAllMocks());
```
