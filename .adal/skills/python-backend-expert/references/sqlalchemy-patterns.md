# SQLAlchemy 2.0 Advanced Patterns

Advanced query patterns, relationship loading, bulk operations, and session management for async SQLAlchemy 2.0 with FastAPI.

---

## Relationship Loading Strategies

### selectinload (Default for Async)

Loads related objects in a separate SELECT with an IN clause. Best for one-to-many and many-to-many relationships.

```python
from sqlalchemy.orm import selectinload

# Load a user with all their posts
result = await session.execute(
    select(User)
    .where(User.id == user_id)
    .options(selectinload(User.posts))
)
user = result.scalar_one_or_none()
# user.posts is loaded — no lazy loading needed
```

**When to use:** Default choice for async. Good when you need the related objects and the collection is moderate-sized.

### joinedload

Loads related objects in a single JOIN query. Best for many-to-one and one-to-one relationships.

```python
from sqlalchemy.orm import joinedload

# Load posts with their authors in a single query
result = await session.execute(
    select(Post)
    .options(joinedload(Post.author))
    .limit(20)
)
posts = result.unique().scalars().all()
# post.author is loaded for each post
```

**Important:** Always call `.unique()` on the result when using `joinedload` with collections, as the JOIN can produce duplicate rows.

**When to use:** For to-one relationships where you always need the related object.

### subqueryload

Loads related objects in a separate subquery. Similar to selectinload but uses a subquery instead of IN.

```python
from sqlalchemy.orm import subqueryload

result = await session.execute(
    select(User)
    .options(subqueryload(User.posts))
)
```

**When to use:** When the parent query is complex and IN clause would be too large.

### Nested Loading

Load relationships of relationships:

```python
result = await session.execute(
    select(User)
    .options(
        selectinload(User.posts).selectinload(Post.comments)
    )
)
```

### raiseload (Prevent Accidental Lazy Loads)

```python
from sqlalchemy.orm import raiseload

result = await session.execute(
    select(User)
    .options(raiseload("*"))  # Raise error on any lazy load attempt
    .options(selectinload(User.posts))  # Explicitly load what you need
)
```

**When to use:** In development/testing to catch N+1 queries early.

---

## Query Optimization

### Selecting Specific Columns

```python
# Only load the columns you need
result = await session.execute(
    select(User.id, User.email, User.display_name)
    .where(User.is_active == True)
)
rows = result.all()  # Returns tuples, not User instances
```

### Aggregation

```python
from sqlalchemy import func

# Count active users
result = await session.execute(
    select(func.count()).select_from(User).where(User.is_active == True)
)
count = result.scalar_one()

# Group by with count
result = await session.execute(
    select(User.role, func.count(User.id).label("count"))
    .group_by(User.role)
)
role_counts = result.all()
```

### Exists Check

```python
from sqlalchemy import exists

# Efficient existence check (doesn't load the row)
result = await session.execute(
    select(exists().where(User.email == email))
)
email_exists = result.scalar_one()
```

### Pagination with Cursor

```python
async def list_users_cursor(
    session: AsyncSession,
    *,
    after_id: int | None = None,
    limit: int = 20,
) -> tuple[list[User], bool]:
    query = select(User).order_by(User.id)

    if after_id is not None:
        query = query.where(User.id > after_id)

    # Fetch one extra to determine has_more
    query = query.limit(limit + 1)

    result = await session.execute(query)
    users = list(result.scalars().all())

    has_more = len(users) > limit
    if has_more:
        users = users[:limit]

    return users, has_more
```

---

## Bulk Operations

### Bulk Insert

```python
from sqlalchemy import insert

# Insert many rows efficiently
users_data = [
    {"email": "a@example.com", "display_name": "Alice", "hashed_password": "..."},
    {"email": "b@example.com", "display_name": "Bob", "hashed_password": "..."},
]
await session.execute(insert(User), users_data)
await session.flush()
```

### Bulk Update

```python
from sqlalchemy import update

# Update many rows at once
await session.execute(
    update(User)
    .where(User.last_login < cutoff_date)
    .values(is_active=False)
)
await session.flush()
```

### Bulk Delete

```python
from sqlalchemy import delete

await session.execute(
    delete(User).where(User.is_active == False)
)
await session.flush()
```

---

## Connection Pool Tuning

```python
engine = create_async_engine(
    database_url,
    pool_size=5,          # Steady-state connections
    max_overflow=10,      # Additional connections under load
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_timeout=30,      # Wait time for available connection
    echo=False,           # Set True for SQL logging in development
)
```

**Guidelines:**
- `pool_size`: Set to expected concurrent database sessions (usually matches web worker count)
- `max_overflow`: Additional connections allowed above pool_size during traffic spikes
- `pool_pre_ping`: Always enable to handle database restarts gracefully
- `pool_recycle`: Set below the database's connection timeout (PostgreSQL default: 8 hours)

---

## Async Session Patterns

### Request-Scoped Session

```python
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        async with session.begin():
            yield session
            # Auto-commits on success, rolls back on exception
```

### Background Task Session

```python
async def send_welcome_email(user_id: int) -> None:
    """Background task — creates its own session."""
    async with async_session_factory() as session:
        async with session.begin():
            user = await session.get(User, user_id)
            if user:
                await email_service.send(user.email, "Welcome!")
```

### Test Session with Rollback

```python
@pytest.fixture
async def db_session(engine):
    async with engine.connect() as conn:
        await conn.begin()
        async_session = AsyncSession(bind=conn, expire_on_commit=False)

        yield async_session

        await async_session.close()
        await conn.rollback()
```

---

## Index Strategy

```python
from sqlalchemy import Index

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Composite index for common query pattern
    __table_args__ = (
        Index("ix_orders_user_status", "user_id", "status"),
        Index(
            "ix_orders_active",
            "user_id", "created_at",
            postgresql_where=(status != "cancelled"),  # Partial index
        ),
    )
```
