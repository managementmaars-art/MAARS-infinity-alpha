# FastAPI Database Operations

## SQLModel Integration (Recommended)

SQLModel is the recommended ORM for FastAPI, combining SQLAlchemy and Pydantic.

### Basic Setup

```python
from sqlmodel import Field, Session, SQLModel, create_engine
from fastapi import Depends, FastAPI, HTTPException
from typing import Annotated

# Database engine
engine = create_engine("postgresql+psycopg://user:pass@localhost/db")

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### Model Definition

```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    hashed_password: str
    disabled: bool = Field(default=False)

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = None
    owner_id: int = Field(foreign_key="user.id")
```

### Session Management with Dependency Injection

```python
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/users/{user_id}")
def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### CRUD Operations

**Create:**
```python
@app.post("/users/", response_model=User)
def create_user(user: User, session: SessionDep):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

**Read with Filtering:**
```python
from sqlmodel import select

@app.get("/users/", response_model=list[User])
def list_users(session: SessionDep, skip: int = 0, limit: int = 100):
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users
```

**Update:**
```python
@app.patch("/users/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```

**Delete:**
```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    return {"ok": True}
```

### Relationships

```python
class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    headquarters: str

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")

# Query with joins
@app.get("/heroes/{hero_id}/team")
def get_hero_with_team(hero_id: int, session: SessionDep):
    statement = select(Hero, Team).where(Hero.id == hero_id).join(Team)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Hero not found")
    return result
```

## Database Best Practices

### 1. Connection Pooling

```python
from sqlmodel import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    pool_size=20,          # Number of connections to maintain
    max_overflow=0,        # Max additional connections
    pool_timeout=30,       # Timeout for getting connection
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

### 2. Async Database Operations

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

async def get_session():
    async with AsyncSession(async_engine) as session:
        yield session

@app.get("/users/{user_id}")
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.get(User, user_id)
    return result
```

### 3. Migrations with Alembic

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add users table"

# Run migrations
alembic upgrade head
```

### 4. Database URL from Environment

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
engine = create_engine(settings.database_url)
```

### 5. Transaction Management

```python
@app.post("/transfer/")
def transfer_funds(transfer: Transfer, session: SessionDep):
    try:
        # Debit from source
        source = session.get(Account, transfer.source_id)
        source.balance -= transfer.amount

        # Credit to destination
        dest = session.get(Account, transfer.dest_id)
        dest.balance += transfer.amount

        session.commit()
        return {"status": "success"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
```

## Neon Serverless PostgreSQL

For serverless deployments, use Neon's connection pooling:

```python
from sqlmodel import create_engine

# Use pooling connection string
engine = create_engine(
    "postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require",
    connect_args={"sslmode": "require"}
)
```

## Testing with In-Memory SQLite

```python
from fastapi.testclient import TestClient

def test_create_user():
    # Use in-memory SQLite for tests
    test_engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    client = TestClient(app)
    response = client.post("/users/", json={"name": "Test", "email": "test@example.com"})
    assert response.status_code == 200
```
