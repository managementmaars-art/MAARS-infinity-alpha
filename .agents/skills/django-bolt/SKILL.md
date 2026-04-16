---
name: django-bolt
description: Build high-performance APIs with Django-Bolt, including BoltAPI routes, typed request validation, msgspec serialization, auth guards, middleware, OpenAPI docs, pagination, streaming, SSE, WebSockets, and testing. Use when the user asks to create a new bolt endpoint, set up a Django-Bolt project, add JWT or API key auth, configure runbolt, wire guards or middleware, add pagination or streaming, generate OpenAPI docs, write TestClient tests, or migrate from FastAPI, Django REST Framework, or Django Ninja to django-bolt. Do NOT use for general Django views, Django admin customization, or standard Django REST Framework work.
compatibility: Skills-compatible coding agents working on Django projects that use django-bolt.
metadata:
  author: Farhan Ali Raza
  category: web-framework
  version: 0.7.0
  tags: [django, django-bolt, api, rust, high-performance, openapi, testing]
---

# Django-Bolt

## Critical rules

- Always use async handlers unless the user explicitly needs sync
- Use async database access in async handlers (e.g., Django async ORM: `aget`, `acreate`, `afilter`)
- Use `msgspec.Struct` for simple typed payloads; use `Serializer` for richer validation and reusable field sets
- Keep route signatures typed -- let Django-Bolt validate inputs instead of hand-parsing `request.body`
- Use built-in HTTP exceptions (`HTTPException`) for expected API failures
- Run with `python manage.py runbolt --dev` for development, not `uvicorn` or `gunicorn`

## Apply this skill when

- The user mentions `django-bolt`, `BoltAPI`, `runbolt`, `Depends`, `response_model`, `APIView`, `JWTAuthentication`, `OpenAPIConfig`, `TestClient`, `WebSocket`, `StreamingResponse`, or `SSE`
- The user wants to start a Django-Bolt app, add endpoints, wire auth, expose docs, add pagination, return files, streams, or SSE events, or test handlers
- The user wants to migrate from FastAPI, DRF, or Django Ninja -- see `references/migration-playbook.md`

## Do NOT apply when

- The user is working with plain Django views, templates, or Django admin
- The user is building a standard DRF API without mentioning django-bolt
- The task is about Django ORM models, migrations, or admin configuration only

## Code examples

### Minimal setup

```python
# settings.py
INSTALLED_APPS = [
    "django_bolt",
]
```

```python
# myproject/api.py
from django_bolt import BoltAPI

api = BoltAPI()


@api.get("/health")
async def health():
    return {"status": "ok"}
```

Run: `python manage.py runbolt --dev`

### BoltAPI constructor options

```python
from django_bolt import (
    BoltAPI,
    CompressionConfig,
    LoggingMiddleware,
    OpenAPIConfig,
    ScalarRenderPlugin,
    TimingMiddleware,
)

api = BoltAPI(
    prefix="/api/v1",                        # URL prefix for all routes
    trailing_slash="strip",                  # "strip", "append", or "keep"
    validate_response=True,                  # validate response_model output
    compression=CompressionConfig(),         # or False to disable
    enable_logging=True,
    middleware=[                              # Python middleware stack
        TimingMiddleware,
        LoggingMiddleware,
    ],
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
        path="/docs",
        render_plugins=[ScalarRenderPlugin()],
        enabled=True,
    ),
)
```

### Route decorators and parameters

All HTTP methods: `@api.get`, `@api.post`, `@api.put`, `@api.patch`, `@api.delete`, `@api.head`, `@api.options`.

```python
import msgspec
from django_bolt import BoltAPI

api = BoltAPI()


class ItemOut(msgspec.Struct):
    id: int
    name: str


@api.get(
    "/items/{item_id}",
    response_model=ItemOut,        # validates and documents the output shape
    status_code=200,               # default status code
    tags=["items"],                # OpenAPI tags
    summary="Get an item",         # OpenAPI summary
    description="Fetch item by ID",
    guards=[],                     # permission guards
    auth=[],                       # auth backends
    validate_response=True,        # validate output matches response_model
)
async def get_item(item_id: int):
    return {"id": item_id, "name": "Widget"}
```

### Typed request body (msgspec.Struct)

```python
import msgspec
from django_bolt import BoltAPI

api = BoltAPI()


class ItemIn(msgspec.Struct):
    name: str
    price: float
    tags: list[str] = []


class ItemOut(msgspec.Struct):
    id: int
    name: str
    price: float


@api.post("/items", response_model=ItemOut, status_code=201)
async def create_item(item: ItemIn):
    return {"id": 1, "name": item.name, "price": item.price}
```

### Serializer with validation

```python
from __future__ import annotations

from typing import Annotated

import msgspec
from django_bolt import BoltAPI
from django_bolt.serializers import Serializer, field_validator, model_validator

api = BoltAPI()


class UserCreate(Serializer):
    username: str
    email: str
    password: Annotated[str, msgspec.Meta(min_length=8)]

    class Config:
        write_only = {"password"}

    @field_validator("email")
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Invalid email")
        return value.lower()

    @model_validator
    def validate_model(self):
        if self.username.lower() == "admin":
            raise ValueError("Username 'admin' is reserved")
        return self


class UserOut(Serializer):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        read_only = {"id"}


@api.post("/users", response_model=UserOut, status_code=201)
async def create_user(data: UserCreate):
    return {"id": 1, "username": data.username, "email": data.email, "is_active": True}
```

### Parameter markers (Query, Header, Cookie, Form, File, Path, Depends)

```python
from __future__ import annotations

from typing import Annotated

import msgspec
from django_bolt import BoltAPI, Depends, UploadFile
from django_bolt.param_functions import Body, Cookie, File, Form, Header, Path, Query

api = BoltAPI()


# Query parameters with validation
@api.get("/search")
async def search(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return {"query": q, "page": page, "limit": limit}


# Grouped query params via msgspec.Struct
class Filters(msgspec.Struct):
    status: str | None = None
    sort: str = "created"
    order: str = "desc"


@api.get("/items")
async def list_items(filters: Annotated[Filters, Query()]):
    return {"status": filters.status, "sort": filters.sort}


# Path parameter with alias
@api.get("/users/{user_id}")
async def get_user(user_id: Annotated[int, Path(ge=1)]):
    return {"user_id": user_id}


# Header extraction
@api.get("/secure")
async def secure(x_api_key: Annotated[str, Header(alias="x-api-key")]):
    return {"key": x_api_key}


# Grouped headers via struct
class APIHeaders(msgspec.Struct):
    authorization: str
    x_request_id: str | None = None  # snake_case auto-maps to X-Request-Id


@api.get("/with-headers")
async def with_headers(headers: Annotated[APIHeaders, Header()]):
    return {"auth": headers.authorization}


# Cookie extraction
@api.get("/preferences")
async def preferences(
    theme: Annotated[str, Cookie()] = "light",
    lang: Annotated[str, Cookie()] = "en",
):
    return {"theme": theme, "lang": lang}


# Form data
@api.post("/login")
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    return {"username": username}


# Grouped form data via struct
class ContactForm(msgspec.Struct):
    name: str
    email: str
    message: str


@api.post("/contact")
async def contact(data: Annotated[ContactForm, Form()]):
    return {"name": data.name, "email": data.email}


# File uploads with validation
from django_bolt import FileSize

@api.post("/upload")
async def upload(
    title: Annotated[str, Form()],
    file: Annotated[
        UploadFile,
        File(max_size=FileSize.MB_30, allowed_types=["application/pdf", "image/*"]),
    ],
):
    content = await file.read()
    return {"title": title, "filename": file.filename, "size": len(content)}


# Multiple file upload
@api.post("/upload-many")
async def upload_many(
    files: Annotated[list[UploadFile], File(max_files=5)],
):
    return {"count": len(files)}


# Dependency injection
async def get_db():
    db = await connect_db()
    try:
        yield db
    finally:
        await db.close()


async def get_current_user(request):
    user_id = request.auth.get("user_id")
    return {"id": user_id, "username": "example"}


@api.get("/profile")
async def profile(
    user: Annotated[dict, Depends(get_current_user)],
):
    return {"id": user["id"], "username": user["username"]}


# Explicit JSON body marker
class UpdatePayload(msgspec.Struct):
    name: str
    value: int


@api.put("/settings")
async def update_settings(data: Annotated[UpdatePayload, Body()]):
    return {"name": data.name}
```

### Response types

```python
from django_bolt import BoltAPI, JSON, Response, StreamingResponse
from django_bolt.responses import FileResponse, HTML, PlainText, Redirect

api = BoltAPI()


# Dict/list returns auto-serialize to JSON
@api.get("/auto-json")
async def auto_json():
    return {"message": "hello"}


# Explicit JSON with custom status
@api.post("/created")
async def created():
    return JSON({"id": 1, "created": True}, status_code=201)


# Response with custom headers and cookies
@api.post("/login")
async def login():
    return (
        Response({"token": "abc"}, status_code=200)
        .set_cookie("session", "xyz", httponly=True, secure=True, samesite="Strict")
        .set_cookie("theme", "dark", max_age=86400)
    )


@api.post("/logout")
async def logout():
    return Response({"ok": True}).delete_cookie("session")


# PlainText
@api.get("/text")
async def text():
    return PlainText("Hello, World!")


# HTML
@api.get("/page")
async def page():
    return HTML("<h1>Hello</h1><p>Welcome to the API</p>")


# Redirect
@api.get("/old-path")
async def old_path():
    return Redirect("/new-path")           # 307 temporary by default


@api.get("/moved")
async def moved():
    return Redirect("/new-location", status_code=301)  # permanent


# File download
@api.get("/download")
async def download():
    return FileResponse(
        "/path/to/report.pdf",
        filename="report.pdf",
        media_type="application/pdf",
    )


# Streaming response
@api.get("/stream")
async def stream():
    async def generate():
        for chunk in ["Hello ", "World ", "!"]:
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
```

### SSE (Server-Sent Events)

```python
import asyncio
import json

from django_bolt import BoltAPI, StreamingResponse, no_compress

api = BoltAPI()


@api.get("/events")
@no_compress  # disable compression for SSE
async def events():
    async def generate():
        for i in range(10):
            data = json.dumps({"count": i, "message": f"event-{i}"})
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)
        yield "event: done\ndata: stream complete\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### WebSocket

```python
from django_bolt import BoltAPI, WebSocket, WebSocketDisconnect

api = BoltAPI()


# Echo server
@api.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message in websocket.iter_text():
            await websocket.send_text(f"Echo: {message}")
    except WebSocketDisconnect:
        pass


# JSON messages
@api.websocket("/ws/chat")
async def chat(websocket: WebSocket, room: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            response = {"room": room, "user": data.get("user"), "text": data.get("text")}
            await websocket.send_json(response)
    except WebSocketDisconnect:
        pass
```

### Authentication and guards

```python
from django_bolt import (
    AllowAny,
    APIKeyAuthentication,
    BoltAPI,
    HasAllPermissions,
    HasAnyPermission,
    HasPermission,
    IsAdminUser,
    IsAuthenticated,
    IsStaff,
    JWTAuthentication,
    Request,
    create_jwt_for_user,
)

api = BoltAPI()


# Generate JWT for a user
@api.post("/auth/login")
async def login(username: str, password: str):
    user = await verify_credentials(username, password)  # your auth logic
    if not user:
        from django_bolt.exceptions import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt_for_user(user)
    return {"access_token": token}


# JWT-protected endpoint
@api.get("/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
async def me(request: Request):
    return {"user_id": request.user.id, "username": request.user.username}


# API key auth
@api.get("/api/data", auth=[APIKeyAuthentication()], guards=[IsAuthenticated()])
async def api_data(request: Request):
    return {"data": "secret"}


# Multiple guards
@api.delete(
    "/admin/users/{user_id}",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated(), IsAdminUser()],
)
async def delete_user(user_id: int):
    await remove_user(user_id)  # your deletion logic
    return {"deleted": user_id}


# Permission-based guards
@api.post(
    "/articles",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated(), HasPermission("blog.add_article")],
)
async def create_article(title: str, body: str):
    return {"title": title}


@api.get(
    "/reports",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated(), HasAnyPermission("reports.view", "reports.export")],
)
async def view_reports():
    return {"reports": []}


@api.post(
    "/deploy",
    auth=[JWTAuthentication()],
    guards=[IsAuthenticated(), HasAllPermissions("deploy.create", "deploy.approve")],
)
async def deploy():
    return {"status": "deploying"}


# Staff-only
@api.get("/staff/dashboard", auth=[JWTAuthentication()], guards=[IsStaff()])
async def staff_dashboard():
    return {"stats": {}}


# Public endpoint (no auth required)
@api.get("/public", guards=[AllowAny()])
async def public():
    return {"public": True}
```

### Middleware (CORS, rate limiting, custom)

```python
from django_bolt import BoltAPI, BaseMiddleware, Request, Response, cors, middleware, no_compress, rate_limit, skip_middleware

api = BoltAPI()


# Per-route CORS
@api.get("/public/data")
@cors(
    origins=["https://example.com", "https://app.example.com"],
    methods=["GET", "POST"],
    headers=["Authorization", "Content-Type"],
    credentials=True,
    max_age=3600,
)
async def public_data():
    return {"data": "accessible cross-origin"}


# Rate limiting
@api.post("/api/expensive")
@rate_limit(rps=10, burst=20, key="ip")
async def expensive_operation():
    return {"result": "ok"}


# Skip specific middleware on a route
@api.get("/internal")
@skip_middleware("compression", "rate_limit")
async def internal():
    return {"internal": True}


# Disable compression for streaming
@api.get("/stream")
@no_compress
async def stream():
    from django_bolt import StreamingResponse
    async def gen():
        yield "chunk1"
        yield "chunk2"
    return StreamingResponse(gen(), media_type="text/plain")


# Custom Python middleware
class RequestTimingMiddleware(BaseMiddleware):
    async def process_request(self, request: Request) -> Response:
        import time
        start = time.perf_counter()
        response = await self.get_response(request)
        elapsed = time.perf_counter() - start
        response.headers["X-Response-Time"] = f"{elapsed:.4f}s"
        return response


# Attach custom middleware to a route
@api.post("/upload")
@middleware(RequestTimingMiddleware)
async def upload(request: Request):
    return {"uploaded": True}
```

### Pagination

```python
from django_bolt import (
    BoltAPI,
    CursorPagination,
    LimitOffsetPagination,
    PageNumberPagination,
    paginate,
)

api = BoltAPI()


# Page-number pagination (default)
# GET /users?page=2&page_size=25
@api.get("/users")
@paginate(PageNumberPagination)
async def list_users(request):
    return await get_all_users()  # return a queryset or list


# Custom page size
class LargePages(PageNumberPagination):
    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"


@api.get("/products")
@paginate(LargePages)
async def list_products(request):
    return await get_active_products()


# Limit-offset pagination
# GET /logs?limit=50&offset=100
@api.get("/logs")
@paginate(LimitOffsetPagination)
async def list_logs(request):
    return await get_all_logs()


# Cursor pagination (best for infinite scroll / real-time feeds)
# GET /feed?cursor=abc123
class FeedPagination(CursorPagination):
    page_size = 20
    ordering = "-created_at"


@api.get("/feed")
@paginate(FeedPagination)
async def feed(request):
    return await get_all_posts()
```

### OpenAPI documentation

```python
from django_bolt import (
    BoltAPI,
    OpenAPIConfig,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
)

# Minimal -- serves Swagger UI at /docs
api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="My API",
        version="1.0.0",
    ),
)

# Full configuration
api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="Acme API",
        version="2.0.0",
        description="The Acme Corp backend API",
        path="/docs",                              # docs URL
        enabled=True,
        render_plugins=[
            SwaggerRenderPlugin(),                  # /docs (default)
            RedocRenderPlugin(),                    # /docs/redoc
            ScalarRenderPlugin(),                   # /docs/scalar
            RapidocRenderPlugin(),                  # /docs/rapidoc
            StoplightRenderPlugin(),                # /docs/stoplight
        ],
        exclude_paths=["/admin", "/static"],
        include_error_responses=True,
        use_handler_docstrings=True,                # use docstrings as descriptions
    ),
)


# Per-route OpenAPI metadata
@api.get(
    "/items",
    tags=["items"],
    summary="List all items",
    description="Returns a paginated list of items with optional filters.",
)
async def list_items():
    """This docstring is also used as the description if use_handler_docstrings=True."""
    return []
```

### Error handling

```python
from django_bolt import BoltAPI
from django_bolt.exceptions import HTTPException

api = BoltAPI()


@api.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await fetch_item(item_id)  # your data access logic
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@api.post("/items")
async def create_item(name: str, price: float):
    if price < 0:
        raise HTTPException(status_code=422, detail="Price must be positive")
    return {"id": 1, "name": name, "price": price}
```

### Testing

```python
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

api = BoltAPI()


@api.get("/hello")
async def hello():
    return {"message": "world"}


@api.post("/items")
async def create_item(name: str, price: float):
    return {"name": name, "price": price}


# Basic usage
with TestClient(api) as client:
    # GET request
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "world"}

    # POST with JSON body
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"

    # Custom headers
    response = client.get("/hello", headers={"X-Request-ID": "test-123"})
    assert response.status_code == 200

    # Test 404
    response = client.get("/nonexistent")
    assert response.status_code == 404
```

### Router composition (multiple api.py files)

```python
# users/api.py
from django_bolt import BoltAPI

api = BoltAPI(prefix="/users")

@api.get("/")
async def list_users():
    return []

@api.get("/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id}
```

```python
# orders/api.py
from django_bolt import BoltAPI

api = BoltAPI(prefix="/orders")

@api.get("/")
async def list_orders():
    return []
```

`runbolt` auto-discovers all `api.py` files in installed apps and the project root. Each `api = BoltAPI()` instance is merged into the unified router automatically.

## Step-by-step workflow

### Step 1: Classify the request

Place the task into one bucket before writing code:

1. **First-time setup** -- new project or first endpoint
2. **New endpoint or CRUD surface** -- adding routes
3. **Auth or permission wiring** -- JWT, API key, guards
4. **Docs, responses, pagination, or testing** -- polish features
5. **Migration** -- porting from FastAPI, DRF, or Django Ninja (see `references/migration-playbook.md`)

### Step 2: Start from the minimal shape

1. Add `"django_bolt"` to `INSTALLED_APPS`
2. Create an `api.py` in the project or app directory
3. Instantiate `BoltAPI()`
4. Add async route handlers with typed parameters
5. Run with `python manage.py runbolt --dev`

If the user already has a Django project, preserve their existing models, admin, apps, and settings.

### Step 3: Choose the right primitives

| Need | Use |
|------|-----|
| Simple JSON body | `msgspec.Struct` |
| Rich validation / reusable fields | `Serializer` with `field_validator` |
| Output shape + docs | `response_model` on the route |
| Path/query/header/cookie/form/file params | Parameter markers from `django_bolt.param_functions` |
| Auth | `JWTAuthentication()`, `APIKeyAuthentication()`, or session auth |
| Permissions | Guards: `IsAuthenticated`, `IsAdminUser`, `IsStaff`, `HasPermission` |
| CRUD organization | `APIView` or function-based routes |
| Real-time | `@api.websocket()` with `WebSocket` |
| One-way live updates | `StreamingResponse(..., media_type="text/event-stream")` |
| API docs | `OpenAPIConfig` (served at `/docs` by default) |
| Tests | `django_bolt.testing.TestClient` |

### Step 4: Write short, copyable examples

- One endpoint per example
- One concept per example
- Minimal imports
- Paste-and-run ready for `api.py`

## Common tasks

### Add auth

- **JWT**: `auth=[JWTAuthentication()]` with guards like `IsAuthenticated()`, `IsStaff()`, `HasPermission("app.perm")`
- **API key**: `auth=[APIKeyAuthentication()]`
- Use `create_jwt_for_user(user)` to generate tokens
- Access the authenticated user via `request.user` inside handlers

### Add validation

- `msgspec.Struct` for simple JSON bodies -- fields are validated automatically
- `Serializer` with `@field_validator` / `@model_validator` for richer checks
- `Annotated[type, Meta(...)]` for field constraints (`min_length`, `max_length`, `ge`, `le`, `pattern`)
- Parameter markers (`Query`, `Header`, `Cookie`, `Form`, `File`, `Depends`) accept validation kwargs directly
- Never manually parse `request.body` -- use typed parameters

### Add CRUD

- Start with function-based `@api.get`, `@api.post`, etc. for small APIs
- Use `@api.view("/path")` with `APIView` when several methods share one resource path

### Add responses and streaming

- Return dicts, lists, or `msgspec.Struct` for JSON (auto-serialized)
- `JSON(data, status_code=201)` for custom status codes
- `Response(data).set_cookie(...)` for headers and cookies
- `PlainText`, `HTML`, `Redirect`, `FileResponse` for other content types
- `StreamingResponse(generator(), media_type="text/event-stream")` for SSE with `data: ...\n\n` chunks
- Use `@no_compress` on streaming endpoints

### Add pagination

- `@paginate(PageNumberPagination)` for page-based (`?page=1&page_size=20`)
- `@paginate(LimitOffsetPagination)` for offset-based (`?limit=20&offset=40`)
- `@paginate(CursorPagination)` for cursor-based (`?cursor=abc`)
- Subclass to customize `page_size`, `max_page_size`, `page_size_query_param`, `ordering`

### Add OpenAPI docs

- Pass `openapi_config=OpenAPIConfig(title="...", version="...")` to `BoltAPI()`
- Use `tags`, `summary`, `description`, `response_model` on route decorators
- Choose render plugin: `SwaggerRenderPlugin`, `RedocRenderPlugin`, `ScalarRenderPlugin`, etc.
- Docs served at `/docs` by default (configurable via `path`)

### Add tests

- Use `TestClient(api)` as a context manager
- Supports `.get()`, `.post()`, `.put()`, `.patch()`, `.delete()` with `json=`, `headers=`, `cookies=`
- Assert `response.status_code`, `.json()`, `.headers`
- Cover validation failures (422) and auth failures (401/403)

## Troubleshooting

### "Module django_bolt not found"

CRITICAL: Ensure `"django_bolt"` is in `INSTALLED_APPS` in `settings.py`. The package is `django-bolt` (hyphen) but the Python module is `django_bolt` (underscore).

### Server won't start with runbolt

1. Verify `python manage.py runbolt --dev` is being used, not `uvicorn` or `gunicorn`
2. Check that the Rust extension is built: run `just build` from the project root
3. Ensure `api.py` exists in the Django project root or in an installed app directory

### Route not found (404)

1. Confirm `api.py` is in a directory `runbolt` discovers: project root (same dir as `settings.py`) or an installed app
2. Verify the `api` variable is a `BoltAPI()` instance named exactly `api`
3. Check route path matches (leading slash required: `/items`, not `items`)

### Auth returns 401 unexpectedly

1. For JWT: verify token is passed in `Authorization: Bearer <token>` header
2. For JWT: check token expiration and secret key configuration
3. For session auth: ensure Django session and auth middleware are enabled
4. For guards: verify the user object has the required permissions/attributes

## References

- Read `references/migration-playbook.md` when porting from FastAPI, DRF, or Django Ninja
