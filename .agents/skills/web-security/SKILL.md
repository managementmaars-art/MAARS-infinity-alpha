---
name: web-security
cluster: web-dev
description: "OWASP Top 10, CSP, CORS, XSS/CSRF prevention, auth patterns, dependency scanning"
tags: ["security","owasp","csp","cors","web"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "web security owasp xss csrf csp cors authentication injection"
---

## web-security

### Purpose
This skill enables developers to implement and audit web security measures based on OWASP Top 10 guidelines, including CSP, CORS, XSS/CSRF prevention, authentication patterns, and dependency scanning. It focuses on protecting web applications from common vulnerabilities like injection attacks and unauthorized access.

### When to Use
Use this skill during web application development, security audits, or deployments. Apply it when building APIs, handling user authentication, configuring cross-origin requests, or scanning dependencies for known vulnerabilities. Ideal for projects using frameworks like Express.js or React, or when integrating third-party libraries.

### Key Capabilities
- **OWASP Top 10 Scanning**: Detects issues like SQL injection and broken authentication; use built-in checks via `openclaw web-security scan --owasp`.
- **CSP Configuration**: Generates Content Security Policy headers; example: set policy with `openclaw web-security csp --policy "default-src 'self'"`
- **CORS Management**: Enforces Cross-Origin Resource Sharing; configure with `openclaw web-security cors --allow "https://example.com"`.
- **XSS/CSRF Prevention**: Provides sanitization functions and token generation; e.g., inject anti-CSRF in code: `const token = generateCSRFToken(); res.setHeader('X-CSRF-Token', token);`
- **Authentication Patterns**: Implements JWT or session-based auth; scan for weaknesses with `openclaw web-security auth --check`.
- **Dependency Scanning**: Analyzes npm/yarn packages for vulnerabilities; run with `openclaw web-security depscan --path ./package.json`.

### Usage Patterns
To accomplish tasks, invoke the skill via OpenClaw's CLI or API. For scanning, provide project paths and flags; for configuration, output directly to code files. Always set environment variables for authentication, e.g., export `$OPENCLAW_API_KEY` before running commands. Example pattern: Pipe output to a file for integration, like `openclaw web-security scan --output report.json`. For code snippets, embed generated security code into your app; e.g., add CSP middleware in Express: `app.use((req, res, next) => { res.setHeader('Content-Security-Policy', "default-src 'self'"); next(); });`

### Common Commands/API
- **CLI Commands**: Use `openclaw web-security [subcommand] [flags]`. For example, scan a project: `openclaw web-security scan --project /path/to/app --key $OPENCLAW_API_KEY`. API endpoint: POST to `/api/web-security/scan` with JSON body `{ "projectPath": "/path/to/app", "apiKey": "$OPENCLAW_API_KEY" }`.
- **Subcommands**:
  - `scan --owasp --verbose`: Runs full OWASP check; outputs vulnerabilities in JSON.
  - `csp --generate --domains example.com`: Creates CSP string; e.g., output: `"Content-Security-Policy: default-src 'self' https://example.com"`.
  - `cors --set --origins "http://localhost:3000"`: Configures CORS in a config file like `{ "origins": ["http://localhost:3000"], "methods": ["GET", "POST"] }`.
  - `auth --pattern jwt`: Generates JWT validation code; snippet: `const jwt = require('jsonwebtoken'); const verify = token => jwt.verify(token, process.env.JWT_SECRET);`.
  - `depscan --format npm`: Scans dependencies; e.g., command: `openclaw web-security depscan --path package.json --output vulnerabilities.txt`.
- **API Endpoints**: All commands map to `/api/web-security/{subcommand}`, requiring authentication via header `Authorization: Bearer $OPENCLAW_API_KEY`. Response format: JSON with keys like `{ "status": "success", "data": { ... } }`.

### Integration Notes
Integrate by wrapping OpenClaw calls in your build scripts or CI/CD pipelines. For example, in a GitHub Actions workflow, add: `run: openclaw web-security scan --project . --key ${{ env.OPENCLAW_API_KEY }}`. Use config files for persistent settings, e.g., a `.openclawrc` file with JSON: `{ "web-security": { "defaultFlags": ["--verbose"], "apiKeyEnv": "OPENCLAW_API_KEY" } }`. If combining with other skills, chain outputs; e.g., use web-security scan results as input for a "web-dev" deployment skill. Ensure API keys are stored securely in env vars like `$OPENCLAW_API_KEY` and never hardcoded.

### Error Handling
Handle errors by checking exit codes and response bodies. Common errors: Authentication failure (HTTP 401) if `$OPENCLAW_API_KEY` is invalid—fix by verifying the key format. Scan failures (e.g., "Project path not found") return code 404; resolve by providing absolute paths. For XSS prevention, if a snippet fails, catch exceptions like: `try { sanitizeInput(userInput); } catch (e) { console.error(e.message); // e.g., "Invalid input detected" }`. Parse JSON responses for error details, e.g., `{ "error": "Vulnerability detected", "code": 400 }`, and retry with corrected flags. Always log errors with timestamps for debugging.

### Concrete Usage Examples
1. **Scan for OWASP Vulnerabilities**: To audit a web app for injection risks, run: `openclaw web-security scan --owasp --project /path/to/app`. This outputs a JSON report; then, fix issues by adding code like: `const safeQuery = db.escape(userInput); db.query(safeQuery);`. Expected output: A list of vulnerabilities, e.g., `{ "injection": ["SQL in login endpoint"] }`.
2. **Configure CSP for XSS Prevention**: To set up CSP in an Express app, use: `openclaw web-security csp --generate --policy "script-src 'self'"`. Integrate the output into your server code: `app.use(helmet.contentSecurityPolicy({ directives: { scriptSrc: ["'self'"] } }));`. This prevents inline scripts, reducing XSS risks.

### Graph Relationships
- Related to cluster: "web-dev" (e.g., shares dependencies for web app builds).
- Connected skills: "auth-management" (for advanced auth patterns), "vulnerability-scanning" (for broader security checks).
- Inverse relationships: Depends on "api-tools" for endpoint testing; provides input to "deployment-pipeline" for secure releases.
