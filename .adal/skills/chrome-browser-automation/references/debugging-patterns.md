# Debugging Patterns

Comprehensive workflows for analyzing console and network errors.

## Error Analysis Workflow

**Standard debugging pattern:**

```
1. Get tab context
   tabs_context_mcp()

2. Read console errors
   read_console_messages(
     tabId=<id>,
     pattern="error|exception|failed",
     onlyErrors=true
   )

3. Read network failures
   read_network_requests(
     tabId=<id>,
     urlPattern="/api/",
     filterStatus=[400, 401, 403, 404, 500, 502, 503]
   )

4. Categorize issues
   - Console errors (runtime, syntax, import)
   - Network failures (auth, CORS, server)
   - Performance issues (slow requests, timeouts)

5. Identify root cause
   - Match error to codebase location
   - Check recent changes
   - Verify environment configuration

6. Propose fix
   - Code changes
   - Configuration updates
   - Dependency fixes
```

## Common Console Error Patterns

### TypeError: Cannot read property 'X' of undefined

**Cause:** Accessing property on null/undefined object

**Console output:**
```
TypeError: Cannot read property 'name' of undefined
  at UserProfile.render (profile.js:42)
```

**Analysis workflow:**
```
1. Read console with pattern="TypeError"
2. Identify file and line: profile.js:42
3. Read file: Read(file_path="profile.js", offset=35, limit=10)
4. Identify missing null check
5. Propose fix: user?.name || 'Unknown'
```

**Fix pattern:**
```javascript
// Before
const name = user.name;  // Fails if user is undefined

// After
const name = user?.name || 'Unknown';
```

### ReferenceError: X is not defined

**Cause:** Using variable before declaration or import

**Console output:**
```
ReferenceError: fetchUser is not defined
  at Dashboard.componentDidMount (dashboard.js:15)
```

**Analysis workflow:**
```
1. Read console with pattern="ReferenceError"
2. Identify missing import/declaration
3. Search codebase: Grep(pattern="fetchUser", type="js")
4. Check if function exists in different file
5. Propose import statement
```

**Fix pattern:**
```javascript
// Before
componentDidMount() {
  fetchUser(this.props.userId);  // Not imported
}

// After
import { fetchUser } from './api';
componentDidMount() {
  fetchUser(this.props.userId);
}
```

### Module not found errors

**Cause:** Missing dependency or incorrect import path

**Console output:**
```
Error: Cannot find module '@/components/Button'
```

**Analysis workflow:**
```
1. Read console with pattern="Cannot find module"
2. Identify import path
3. Check if file exists: Glob(pattern="**/Button.{js,jsx,ts,tsx}")
4. Verify path alias configuration
5. Check package.json for missing dependency
```

**Fix patterns:**
```javascript
// Wrong path alias
import Button from '@/components/Button';

// Check actual location
// If in src/ui/components/Button.jsx:
import Button from '@/ui/components/Button';

// Or if missing dependency:
// npm install button-component
```

### SyntaxError in parsed code

**Cause:** JSX in non-transpiled context, trailing commas, etc.

**Console output:**
```
SyntaxError: Unexpected token '<'
  at Object../src/App.js (App.js:10)
```

**Analysis workflow:**
```
1. Read console with pattern="SyntaxError"
2. Check build configuration (webpack, babel)
3. Verify file extension (.jsx vs .js)
4. Check babel plugins for JSX support
```

## Common Network Error Patterns

### 401 Unauthorized

**Cause:** Missing or expired authentication token

**Network output:**
```
GET /api/user/profile → 401 Unauthorized
Headers:
  Authorization: Bearer eyJ... (expired token)
```

**Analysis workflow:**
```
1. Read network requests with filterStatus=[401]
2. Check request headers for auth token
3. Check token expiration
4. Verify token refresh logic
5. Check auth state management
```

**Fix pattern:**
```javascript
// Before
fetch('/api/user/profile', {
  headers: { Authorization: `Bearer ${oldToken}` }
});

// After
const token = await refreshTokenIfExpired(currentToken);
fetch('/api/user/profile', {
  headers: { Authorization: `Bearer ${token}` }
});
```

### 403 Forbidden

**Cause:** Valid auth but insufficient permissions

**Network output:**
```
DELETE /api/admin/users/123 → 403 Forbidden
Response: { "error": "Requires admin role" }
```

**Analysis workflow:**
```
1. Read network requests with filterStatus=[403]
2. Check user role/permissions
3. Verify UI should allow this action
4. Check if feature flag or permission check missing
```

**Fix pattern:**
```javascript
// Add permission check before showing delete button
{user.role === 'admin' && (
  <button onClick={deleteUser}>Delete</button>
)}
```

### 404 Not Found

**Cause:** Wrong API endpoint or missing route

**Network output:**
```
POST /api/users/create → 404 Not Found
```

**Analysis workflow:**
```
1. Read network requests with filterStatus=[404]
2. Verify API endpoint exists in backend
3. Check API documentation
4. Look for typos in URL
5. Verify API version or base URL
```

**Fix pattern:**
```javascript
// Before
fetch('/api/users/create', { method: 'POST', ... });

// After (check API docs)
fetch('/api/v1/users', { method: 'POST', ... });
```

### 500 Internal Server Error

**Cause:** Backend exception or bug

**Network output:**
```
POST /api/orders → 500 Internal Server Error
Response: { "error": "Database connection failed" }
```

**Analysis workflow:**
```
1. Read network requests with filterStatus=[500, 502, 503]
2. Check response body for error details
3. Check backend logs (if accessible)
4. Verify request payload is valid
5. Report to backend team with reproduction steps
```

**Documentation pattern:**
```
Server Error Report:
- Endpoint: POST /api/orders
- Status: 500
- Response: "Database connection failed"
- Request payload: { orderId: 123, items: [...] }
- Reproduction: Submit order with 10+ items
```

### CORS Errors

**Cause:** Cross-origin request blocked by browser

**Console output:**
```
Access to fetch at 'https://api.example.com' from origin 'http://localhost:3000'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header present.
```

**Analysis workflow:**
```
1. Read console with pattern="CORS|Access-Control"
2. Identify origin mismatch
3. Check if backend allows origin
4. Verify preflight OPTIONS request
5. Check proxy configuration for local dev
```

**Fix patterns:**
```javascript
// Backend fix (Express example)
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));

// Frontend proxy (package.json)
{
  "proxy": "https://api.example.com"
}

// Fetch with credentials
fetch('/api/data', { credentials: 'include' });
```

## Performance Debugging

### Slow Network Requests

**Analysis workflow:**
```
1. Read network requests (all)
2. Check timing data:
   - DNS lookup
   - Connection time
   - Time to first byte (TTFB)
   - Content download
3. Identify slow endpoints (>1000ms)
4. Check if caching headers present
5. Verify request size (large payloads)
```

**Network timing analysis:**
```javascript
read_network_requests(tabId=<id>)

// Check timing for each request:
// - waiting: Time to first byte
// - receiving: Download time
// Total > 1000ms = investigate
```

**Common slow request causes:**
- N+1 query pattern (multiple sequential API calls)
- Large response payloads (missing pagination)
- No caching headers (refetching same data)
- Unoptimized database queries

### Memory Leaks

**Console pattern:**
```
Warning: React detects memory leak in <Component>
```

**Analysis workflow:**
```
1. Read console with pattern="memory|leak"
2. Check for uncleared intervals/timeouts
3. Verify event listeners removed
4. Check for unreleased subscriptions
5. Look for retained DOM references
```

**Fix pattern:**
```javascript
// Before (leak)
useEffect(() => {
  const interval = setInterval(fetch, 1000);
  // Missing cleanup
}, []);

// After (no leak)
useEffect(() => {
  const interval = setInterval(fetch, 1000);
  return () => clearInterval(interval);
}, []);
```

## Advanced Debugging Patterns

### Sequential Request Failures

**Pattern:** First request succeeds, subsequent fail

**Analysis:**
```
1. Read all network requests in order
2. Identify pattern:
   - Request 1: POST /auth/login → 200 OK
   - Request 2: GET /api/data → 401 Unauthorized
3. Hypothesis: Auth token not stored/sent
4. Check request headers for token
5. Verify token storage (localStorage, cookies)
```

### Race Conditions

**Pattern:** Intermittent failures based on timing

**Console output:**
```
Error: Cannot update state on unmounted component
```

**Analysis:**
```
1. Read console with pattern="unmounted|race"
2. Identify async operations (fetch, setTimeout)
3. Check for missing cleanup or cancellation
4. Look for state updates after component unmount
```

**Fix pattern:**
```javascript
// Before (race condition)
useEffect(() => {
  fetchData().then(data => setState(data));
}, []);

// After (cleanup)
useEffect(() => {
  let cancelled = false;
  fetchData().then(data => {
    if (!cancelled) setState(data);
  });
  return () => { cancelled = true; };
}, []);
```

### Cascading Failures

**Pattern:** One error triggers many subsequent errors

**Analysis:**
```
1. Read console (all errors)
2. Sort by timestamp
3. Identify first error (root cause)
4. Check if subsequent errors are consequences
5. Fix root cause, verify others disappear
```

**Example:**
```
[10:00:01] Error: Failed to fetch user config
[10:00:01] TypeError: Cannot read 'theme' of undefined
[10:00:01] ReferenceError: themeColor is not defined
[10:00:02] Error: Preferences not loaded

Root cause: Failed config fetch
Fix: Handle fetch failure gracefully
Result: All subsequent errors prevented
```

## Debugging Checklist

Before reporting "no errors found":

- [ ] Console errors checked (onlyErrors=true)
- [ ] Console warnings checked (pattern="warn")
- [ ] Network failures checked (4xx and 5xx status)
- [ ] Network timing checked (slow requests >1000ms)
- [ ] CORS errors checked (pattern="CORS")
- [ ] Memory warnings checked (pattern="memory")
- [ ] React warnings checked (pattern="React|Warning")
- [ ] Source maps verified (error locations accurate)

## Integration with Code Fixes

**Complete debugging workflow:**

```
1. Detect error in browser
   read_console_messages(tabId=<id>, onlyErrors=true)

2. Locate in codebase
   Grep(pattern="error location", type="js")

3. Read relevant code
   Read(file_path="<file>", offset=<line-10>, limit=20)

4. Identify fix
   - Add null check
   - Fix import
   - Update API endpoint

5. Apply fix
   Edit(file_path="<file>", old_string=<buggy>, new_string=<fixed>)

6. Verify in browser
   navigate(url="http://localhost:3000", tabId=<id>)
   read_console_messages(tabId=<id>, onlyErrors=true)

7. Confirm resolution
   Report: "Fixed TypeError in profile.js:42, no console errors"
```

## Example Debug Session

**User:** "The dashboard is broken"

**Workflow:**
```
1. Get context
   tabs_context_mcp()
   navigate(url="http://localhost:3000/dashboard", tabId=<id>)

2. Check console
   read_console_messages(tabId=<id>, onlyErrors=true)
   → TypeError: Cannot read 'map' of undefined at dashboard.js:25

3. Check network
   read_network_requests(tabId=<id>, urlPattern="/api/")
   → GET /api/dashboard/widgets → 401 Unauthorized

4. Diagnose
   - Root cause: API request failed (401)
   - Consequence: Data undefined, .map() fails

5. Check auth
   Read request headers → Authorization header missing

6. Locate bug
   Grep(pattern="dashboard/widgets", type="js")
   → Found in src/components/Dashboard.jsx:15

7. Read code
   Read(file_path="src/components/Dashboard.jsx", offset=10, limit=10)
   → fetch('/api/dashboard/widgets') // Missing auth header

8. Fix
   Edit(file_path="src/components/Dashboard.jsx",
     old_string='fetch(\'/api/dashboard/widgets\')',
     new_string='fetch(\'/api/dashboard/widgets\', {
       headers: { Authorization: `Bearer ${token}` }
     })'
   )

9. Verify
   navigate(url="http://localhost:3000/dashboard", tabId=<id>)
   read_console_messages(tabId=<id>, onlyErrors=true)
   → No errors

10. Report
    "Fixed 401 error by adding Authorization header.
     Dashboard now loads successfully with no console errors."
```
