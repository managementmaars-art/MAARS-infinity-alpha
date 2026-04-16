# Dependency Injection Patterns

Advanced FastAPI dependency injection patterns for authentication, authorization, resource management, and testing.

---

## Pattern 1: Authentication Chain

Build a chain from token extraction to authorized user:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Decode JWT and load user from database."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """Verify user account is active."""
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    return user
```

---

## Pattern 2: Role-Based Access Factory

Create parameterized dependencies with a factory function:

```python
def require_role(*allowed_roles: str):
    """Factory: creates a dependency that checks user roles."""
    async def _check_role(
        user: User = Depends(get_current_active_user),
    ) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {' or '.join(allowed_roles)}",
            )
        return user
    return _check_role


# Usage
@router.get("/admin/dashboard")
async def admin_dashboard(
    admin: User = Depends(require_role("admin")),
) -> dict:
    ...

@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    user: User = Depends(require_role("admin", "editor")),
) -> PostResponse:
    ...
```

---

## Pattern 3: Resource Ownership Check

Verify the authenticated user owns the resource:

```python
def require_ownership(resource_type: str):
    """Factory: checks that the current user owns the resource."""
    async def _check_ownership(
        resource_id: int,
        user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_async_session),
    ) -> User:
        # Dynamic lookup based on resource type
        model_map = {"post": Post, "comment": Comment}
        model = model_map.get(resource_type)
        if model is None:
            raise ValueError(f"Unknown resource type: {resource_type}")

        resource = await session.get(model, resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail=f"{resource_type} not found")
        if resource.user_id != user.id and user.role != "admin":
            raise HTTPException(status_code=403, detail="Not the owner")
        return user
    return _check_ownership


@router.delete("/posts/{resource_id}")
async def delete_post(
    resource_id: int,
    user: User = Depends(require_ownership("post")),
) -> None:
    ...
```

---

## Pattern 4: Pagination Parameters

Reusable pagination dependency:

```python
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    cursor: str | None = None
    limit: int = Field(default=20, ge=1, le=100)


async def get_pagination(
    cursor: str | None = None,
    limit: int = 20,
) -> PaginationParams:
    return PaginationParams(cursor=cursor, limit=min(max(limit, 1), 100))


@router.get("/posts")
async def list_posts(
    pagination: PaginationParams = Depends(get_pagination),
) -> PostListResponse:
    ...
```

---

## Pattern 5: Yield Dependencies (Resource Lifecycle)

Use `yield` for dependencies that need cleanup:

```python
import httpx
from collections.abc import AsyncGenerator


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP client with automatic cleanup."""
    async with httpx.AsyncClient(
        base_url="https://api.example.com",
        timeout=30.0,
        headers={"Accept": "application/json"},
    ) as client:
        yield client
    # Client is closed after response is sent


@router.get("/external-data")
async def fetch_external(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> dict:
    response = await client.get("/data")
    return response.json()
```

---

## Pattern 6: Cached Dependencies

FastAPI caches dependency results per request by default:

```python
# Both services get the SAME session instance (cached per request)
@router.post("/transfer")
async def transfer(
    user_service: UserService = Depends(get_user_service),    # Uses session A
    order_service: OrderService = Depends(get_order_service),  # Uses session A (same!)
) -> TransferResponse:
    # Both services share the same transaction
    ...
```

To get separate instances, disable caching:

```python
async def get_random_id() -> str:
    return str(uuid.uuid4())

@router.get("/test")
async def test(
    id1: str = Depends(get_random_id),                       # Same value
    id2: str = Depends(get_random_id),                       # Same value (cached!)
    id3: str = Depends(get_random_id, use_cache=False),      # Different value
) -> dict:
    return {"id1": id1, "id2": id2, "id3": id3}
```

---

## Pattern 7: Overriding Dependencies in Tests

```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import User


@pytest.fixture
def mock_admin_user():
    return User(id=1, email="admin@test.com", role="admin", is_active=True)


@pytest.fixture
async def client(mock_admin_user):
    """Test client with mocked auth."""

    async def override_current_user():
        return mock_admin_user

    app.dependency_overrides[get_current_user] = override_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

---

## Pattern 8: API Key Authentication

Alternative to JWT for service-to-service communication:

```python
from fastapi import Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(
    api_key: str = Security(api_key_header),
) -> str:
    if api_key not in settings.valid_api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


@router.get("/internal/metrics", dependencies=[Depends(verify_api_key)])
async def get_metrics() -> dict:
    ...
```

---

## Dependency Resolution Order

```
Route handler parameters resolved left-to-right:
  @router.get("/")
  async def handler(
      a: A = Depends(get_a),     # 1st: resolved
      b: B = Depends(get_b),     # 2nd: resolved
      c: C = Depends(get_c),     # 3rd: resolved
  ):

Nested dependencies resolved depth-first:
  get_a depends on get_x, get_y
  Resolution: get_x → get_y → get_a → get_b → get_c

Shared dependencies resolved once (cached):
  If get_a and get_b both depend on get_session,
  get_session is called once and the result is shared.
```
