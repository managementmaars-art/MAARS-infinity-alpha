# Error Catalog

Detailed solutions for common deployment errors.

## Diagnostic Flowchart

Use this decision tree to quickly find the right error category:

```
Deploy failed?
├── Error mentions "token", "auth", or "permission"?
│   └── Go to: Authentication Errors
├── Error mentions "module not found", "TypeScript", or "syntax"?
│   └── Go to: Build Errors
├── Error mentions "bundle size" or "50MB"?
│   └── Go to: Bundle Errors
├── Error mentions "429", "timeout", or "network"?
│   └── Go to: Network Errors
├── Error mentions "webflow.json", "no components", or "invalid JSON"?
│   └── Go to: Configuration Errors
├── Component deployed but not rendering or missing styles?
│   └── Go to: Runtime Errors
├── Error mentions "heap", "memory", or "JavaScript heap"?
│   └── Go to: Memory Errors
└── None of the above?
    └── Go to: Still Broken? (bottom of this file)
```

---

## Authentication Errors

### "Authentication failed"

**Error:**
```
Error: Authentication failed. Please check your API token.
```

**Causes:**
1. Invalid API token
2. Expired token
3. Token from wrong workspace
4. Missing token

**Solution:**
```
🔧 Fix: Authentication Failed

**Step 1: Regenerate API Token**

1. Go to Webflow Dashboard
2. Navigate to Workspace Settings
3. Find "Apps & Integrations" → "Manage"
4. Under "Workspace API Access":
   - Revoke existing token (if any)
   - Click "Generate API Token"
   - Copy the new token

**Step 2: Update Token**

Option A - Environment variable:
```bash
export WEBFLOW_WORKSPACE_API_TOKEN=your-new-token
```

Option B - .env file:
```
WEBFLOW_WORKSPACE_API_TOKEN=your-new-token
```

**Step 3: Retry Deploy**
```bash
npx webflow library share
```

**Verification:**
Token should start with something like `wf_...`
```

---

### "Insufficient permissions"

**Error:**
```
Error: Insufficient permissions to access this workspace.
```

**Solution:**
```
🔧 Fix: Insufficient Permissions

Your API token doesn't have the required permissions.

**Check:**
1. Token is from the correct workspace
2. You have admin/editor role in that workspace
3. Token hasn't been revoked

**If you're not the workspace owner:**
Contact your workspace admin to either:
- Generate a token for you
- Give you the appropriate role

**Generate new token with correct workspace:**
1. Make sure you're in the right workspace in Webflow
2. Go to Workspace Settings → Apps & Integrations
3. Generate new API token
```

---

## Build Errors

### "Module not found"

**Error:**
```
Module not found: Error: Can't resolve '@webflow/react'
```

**Solution:**
```
🔧 Fix: Module Not Found

Missing required dependency.

**Install missing package:**
```bash
npm install --save-dev @webflow/react
```

**If still failing, install all Webflow packages:**
```bash
npm install --save-dev @webflow/webflow-cli @webflow/data-types @webflow/react
```

**Then retry:**
```bash
npx webflow library share
```
```

---

### "TypeScript errors"

**Error:**
```
error TS2345: Argument of type 'X' is not assignable to parameter of type 'Y'.
```

**Solution:**
```
🔧 Fix: TypeScript Error

There's a type mismatch in your code.

**Common causes:**

1. **Wrong prop type:**
   ```typescript
   // ❌ Passing string when number expected
   <Component count="5" />

   // ✅ Correct type
   <Component count={5} />
   ```

2. **Missing prop:**
   ```typescript
   // ❌ Missing required prop
   <Component />

   // ✅ Include required prop
   <Component title="Hello" />
   ```

3. **Incorrect import:**
   ```typescript
   // ❌ Wrong import
   import { props } from "@webflow/react";

   // ✅ Correct import
   import { props } from "@webflow/data-types";
   ```

**To find the error:**
```bash
npx tsc --noEmit
```

This will show you exactly which file and line has the issue.
```

---

### "Unexpected token"

**Error:**
```
SyntaxError: Unexpected token '<'
```

**Solution:**
```
🔧 Fix: Syntax Error

Usually means JSX in a file that doesn't support it.

**Check:**

1. **File extension is correct:**
   - `.tsx` for TypeScript + JSX
   - `.jsx` for JavaScript + JSX
   - `.ts` for TypeScript (no JSX)

2. **tsconfig.json has JSX support:**
   ```json
   {
     "compilerOptions": {
       "jsx": "react-jsx"
     }
   }
   ```

3. **No syntax errors in JSX:**
   ```typescript
   // ❌ Common mistake - missing closing tag
   <div>
     <span>Hello
   </div>

   // ✅ Correct
   <div>
     <span>Hello</span>
   </div>
   ```
```

---

## Bundle Errors

### "Bundle size exceeds limit"

**Error:**
```
Error: Bundle size (62MB) exceeds the 50MB limit.
```

**Solution:**
```
🔧 Fix: Bundle Too Large

Your component library is over the 50MB limit.

**Step 1: Identify large dependencies**
```bash
npx webpack-bundle-analyzer dist/stats.json
```

Or check manually:
```bash
du -sh node_modules/* | sort -rh | head -20
```

**Step 2: Optimize**

Common culprits and alternatives:

| Heavy Package | Size | Alternative |
|--------------|------|-------------|
| moment | ~300KB | date-fns (~30KB) |
| lodash | ~530KB | lodash-es (tree-shakeable) |
| three.js | ~600KB | Dynamic import |
| @mui/material | ~500KB | Individual imports |

**Step 3: Tree-shake imports**

```typescript
// ❌ Imports entire library
import { Button, Card } from "@mui/material";

// ✅ Tree-shakeable
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
```

**Step 4: Lazy load heavy components**

```typescript
import { lazy, Suspense } from "react";

const HeavyComponent = lazy(() => import("./HeavyComponent"));

export const MyComponent = () => (
  <Suspense fallback={<div>Loading...</div>}>
    <HeavyComponent />
  </Suspense>
);
```

**Step 5: Remove unused dependencies**

```bash
npx depcheck
```
```

---

## Runtime Errors

### "Component not rendering"

**Problem:** Component appears in Designer but shows nothing

**Solution:**
```
🔧 Fix: Component Not Rendering

**Check 1: Build errors**
```bash
npx webflow library bundle --public-path http://localhost:4000/
```
Look for any errors in output.

**Check 2: Console errors**
1. Open Designer
2. Open browser DevTools (F12)
3. Check Console tab for errors

**Check 3: SSR issues**
If using browser APIs without guards:

```typescript
// ❌ Will break during SSR
export const Component = () => {
  const width = window.innerWidth;
  return <div>{width}</div>;
};

// ✅ SSR-safe
export const Component = () => {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    setWidth(window.innerWidth);
  }, []);

  return <div>{width || "Loading..."}</div>;
};
```

Or disable SSR:
```typescript
declareComponent(Component, {
  options: { ssr: false }
});
```

**Check 4: Missing root element**
Component must return a single root:

```typescript
// ❌ Multiple roots
export const Component = () => (
  <>
    <div>One</div>
    <div>Two</div>
  </>
);

// ✅ Single root
export const Component = () => (
  <div>
    <div>One</div>
    <div>Two</div>
  </div>
);
```
```

---

### "Styles not appearing"

**Problem:** Component renders but has no styling

**Solution:**
```
🔧 Fix: Missing Styles

**Cause:** Styles not imported in .webflow.tsx file

**Check 1: Import styles in definition file**

```typescript
// Button.webflow.tsx
import { declareComponent } from "@webflow/react";
import { Button } from "./Button";
import "./Button.module.css";  // ← Must be here!

declareComponent(Button, { ... });
```

**Check 2: Not using site classes**
Site classes don't work in Shadow DOM:

```css
/* ❌ Won't work */
.w-button { }

/* ✅ Use your own classes */
.my-button { }
```

**Check 3: styled-components needs decorator**

```typescript
// globals.ts
import { styledComponentsShadowDomDecorator } from "@webflow/styled-components-utils";
export const decorators = [styledComponentsShadowDomDecorator];
```

```json
// webflow.json
{
  "library": {
    "globals": "./src/globals.ts"
  }
}
```

**Check 4: Emotion needs decorator**

```typescript
// globals.ts
import { emotionShadowDomDecorator } from "@webflow/emotion-utils";
export const decorators = [emotionShadowDomDecorator];
```

Then reference globals in webflow.json (same as Check 3).

**Check 5: Tailwind CSS needs globals setup**

1. Ensure `globals.css` contains `@import "tailwindcss";`
2. Ensure `globals.ts` imports `globals.css`:
   ```typescript
   // globals.ts
   import "./globals.css";
   ```
3. Ensure `webflow.json` references the globals file:
   ```json
   {
     "library": {
       "globals": "./src/globals.ts"
     }
   }
   ```
4. Ensure PostCSS is configured with `@tailwindcss/postcss` in `postcss.config.mjs`
```

---

## Configuration Errors

### "webflow.json not found"

**Solution:**
```
🔧 Fix: Missing webflow.json

Create webflow.json in your project root:

```json
{
  "library": {
    "name": "My Component Library",
    "components": ["./src/**/*.webflow.tsx"]
  }
}
```

**Full configuration options:**

```json
{
  "library": {
    "name": "My Component Library",
    "components": ["./src/**/*.webflow.tsx"],
    "globals": "./src/globals.ts",
    "bundleConfig": "./webpack.webflow.js"
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Library name in Designer |
| components | Yes | Glob pattern for .webflow.tsx files |
| globals | No | Path to globals/decorators |
| bundleConfig | No | Custom webpack config |
```

---

### "No components found"

**Error:**
```
Warning: No components found matching pattern "./src/**/*.webflow.tsx"
```

**Solution:**
```
🔧 Fix: No Components Found

**Check 1: File extension**
Files must end with `.webflow.tsx` (not `.webflow.ts` or `.tsx`)

**Check 2: File location**
Files must match the glob pattern in webflow.json

Example pattern: `"./src/**/*.webflow.tsx"`
Valid locations:
- ./src/Button.webflow.tsx ✅
- ./src/components/Button.webflow.tsx ✅
- ./components/Button.webflow.tsx ❌ (not in src/)

**Check 3: declareComponent is called**
Each file must call declareComponent:

```typescript
import { declareComponent } from "@webflow/react";
import { Button } from "./Button";

declareComponent(Button, {  // ← Required!
  name: "Button"
});
```

**Check 4: List your files**
```bash
find . -name "*.webflow.tsx"
```
```

---

### "Invalid JSON in webflow.json"

**Error:**
```
SyntaxError: Unexpected token in webflow.json
```

**Causes:**
1. Trailing commas in JSON
2. Comments in JSON (not allowed)
3. Missing quotes around keys or values
4. Unescaped special characters

**Solution:**
```
🔧 Fix: Invalid JSON

**Step 1: Validate JSON syntax**
```bash
node -e "JSON.parse(require('fs').readFileSync('webflow.json','utf8'))"
```

**Step 2: Common fixes**

```json
// ❌ Trailing comma
{ "library": { "name": "My Lib", } }

// ❌ Comments not allowed
{ "library": { "name": "My Lib" /* comment */ } }

// ✅ Valid JSON
{ "library": { "name": "My Lib" } }
```

**Step 3: Use a JSON validator**
Paste your webflow.json contents into a JSON validator or use your editor's JSON formatting.
```

---

## Network Errors

### "Rate limiting (HTTP 429)"

**Error:**
```
Error: 429 Too Many Requests
```

**Causes:**
1. Too many consecutive `library share` calls
2. Automated scripts hitting the API too frequently

**Solution:**
```
🔧 Fix: Rate Limited

**Step 1: Wait and retry**
Wait 60 seconds before retrying:
```bash
sleep 60 && npx webflow library share
```

**Step 2: For CI/CD pipelines**
Add retry logic with exponential backoff. Avoid deploying on every commit — use branch-based triggers (e.g., only deploy on push to `main`).
```

---

### "Network timeout"

**Error:**
```
Error: Request timed out
Error: ETIMEDOUT
Error: ECONNREFUSED
```

**Causes:**
1. Poor network connectivity
2. Corporate proxy or firewall blocking requests
3. Webflow API outage

**Solution:**
```
🔧 Fix: Network Timeout

**Step 1: Check connectivity**
```bash
curl -I https://api.webflow.com
```

**Step 2: Check for proxy/firewall**
If behind a corporate proxy, configure npm:
```bash
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080
```

**Step 3: Check Webflow status**
Visit the Webflow status page for any ongoing outages.

**Step 4: Retry with verbose output**
```bash
npx webflow library share --verbose
```
```

---

## Memory Errors

### "JavaScript heap out of memory"

**Error:**
```
FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory
```

**Causes:**
1. Very large bundle with many components or heavy dependencies
2. Insufficient default Node.js memory allocation

**Solution:**
```
🔧 Fix: Heap Out of Memory

**Step 1: Increase Node.js memory**
```bash
NODE_OPTIONS="--max-old-space-size=4096" npx webflow library share
```

**Step 2: Reduce bundle size**
If the problem persists, your bundle may be too large:
- Check bundle size: `npx webflow library bundle --public-path http://localhost:4000/`
- Remove unused dependencies: `npx depcheck`
- Tree-shake imports (use specific imports instead of barrel imports)

**Step 3: For CI/CD**
Add the NODE_OPTIONS environment variable to your CI config.
```

---

## Dependency Errors

### "Circular dependency warnings"

**Error:**
```
WARNING: Circular dependency detected: src/components/A.tsx -> src/components/B.tsx -> src/components/A.tsx
```

**Causes:**
1. Component A imports Component B, which imports Component A
2. Shared utility files creating import cycles

**Solution:**
```
🔧 Fix: Circular Dependencies

**Step 1: Identify the cycle**
The warning message shows the exact import chain. Trace the imports.

**Step 2: Break the cycle**
Common patterns:

1. **Extract shared code** into a separate file that both components import
2. **Use dynamic imports** for one direction of the dependency:
   ```typescript
   const ComponentB = lazy(() => import("./ComponentB"));
   ```
3. **Restructure** — if two components depend on each other, they may belong in the same file or need a shared parent

**Step 3: Verify**
```bash
npx webflow library bundle --public-path http://localhost:4000/
```
Confirm the warning is gone.
```

---

## Still Broken?

If none of the solutions above resolve your issue, gather the following information before escalating:

### Data to Collect

```bash
# 1. Recent deploy logs
npx webflow library log

# 2. Verbose deploy output
npx webflow library share --verbose

# 3. Node.js version
node -v

# 4. Package versions
npm list @webflow/webflow-cli @webflow/data-types @webflow/react

# 5. webflow.json contents
cat webflow.json
```

### Where to Get Help

1. **Webflow Community Forum** — Search for your error message; many common issues are already answered
2. **Webflow Support** — Contact with the collected data above
3. **GitHub Issues** — For CLI-specific bugs, check the Webflow CLI repository
