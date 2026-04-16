# Preview URLs

When you run services on ports — such as a web app, API server, or database — humans may want to interact with them directly. You can expose your locally running services as public preview URLs.

## Running Services for Preview

Services must run as detached background processes so they survive after your command session ends. Do not leave them attached to a foreground terminal.

Some potential methods:
```bash
# Start a detached service with logging
setsid -f bash -lc 'cd /path/to/app && exec yarn dev >> /tmp/app.log 2>&1'

# For daemons like Docker
nohup dockerd > /tmp/dockerd.log 2>&1 &
```

After starting a service:
1. Verify the process is running: `pgrep -af 'yarn dev'`
2. Check logs for readiness: `tail -f /tmp/app.log`
3. Confirm it's actually serving: `curl -s http://localhost:3000` (or appropriate health check)
4. Only create the preview after the service is healthy

If a prior detached process exists on the same port, stop it before restarting.

## Creating Previews

```bash
# Expose a local port as a public URL
replicas preview create <port>

# Expose a port with authentication (requires Replicas login to access)
replicas preview create <port> --authenticated

# List all active preview URLs
replicas preview list
```

The `create` command prints the public URL. You can also read all active previews from `~/.replicas/preview-ports.json`.

## Authenticated vs Unauthenticated Previews

Previews can optionally require cookie-based authentication. When `--authenticated` is set, only users who are logged in to replicas.dev can access the preview.

**When to use `--authenticated`:**
- Frontends / web apps that humans will view directly in their browser. Since the user is already logged in to replicas.dev, the auth cookie is automatically present and the preview works seamlessly.

**When NOT to use `--authenticated`:**
- Backend APIs and other services that are called by frontend code. The frontend runs in the user's browser under a different origin, so it cannot forward the Replicas auth cookie to the backend. Making backends authenticated will cause cross-service requests to fail with 401 errors.

**Rule of thumb:** Make frontend previews authenticated, leave backend/API previews unauthenticated.

## Cross-Service References

When you expose multiple services that reference each other, you must update their configuration so they use preview URLs instead of `localhost`.

**Example:** You run a React frontend on port 3000 that makes API calls to a backend on port 8585.

1. Create previews for both:
   ```bash
   replicas preview create 8585
   # Output: https://8585-<hash>.replicas.dev
   replicas preview create 3000 --authenticated
   # Output: https://3000-<hash>.replicas.dev
   ```

2. Update the frontend's environment so its API base URL points to the backend's **preview URL**, not `localhost:8585`. For example, set `REACT_APP_API_URL=https://8585-<hash>.replicas.dev` or update the relevant config file.

**Why?** The frontend works on `localhost` for you because both services run on the same machine. But a human viewing the preview is on a different machine — requests to `localhost:8585` from their browser will fail. They need the public preview URL instead.

## When to Create Previews

- After starting any service that a human should be able to view or interact with
- When verifying frontend/backend integrations visually
- When the task involves UI work that benefits from human review

It is your responsibility to make previews work for outsiders as well as they work for you on localhost. If at any time you need to see the public URLs that have been created, read `~/.replicas/preview-ports.json`.
