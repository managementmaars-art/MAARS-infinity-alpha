---
name: graphql-api
description: GraphQL schema design, resolvers, DataLoaders, subscriptions, Strawberry Python, and performance optimization.
---

# GraphQL API

## Overview

GraphQL provides a typed query language for APIs with a single endpoint. It enables precise data fetching, real-time subscriptions, and self-documenting schemas. Strawberry is the modern Python-first GraphQL library.

## Strawberry Python Setup

```bash
pip install strawberry-graphql[fastapi,debug-server]
pip install strawberry-graphql[channels]  # For subscriptions
```

```python
# main.py
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

# Schema definition
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"

schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema, graphiql=True)

app = FastAPI()
app.include_router(graphql_router, prefix="/graphql")
```

## Schema Design

```python
import strawberry
from strawberry import auto
from strawberry.types import Info
from typing import Optional, List
from datetime import datetime
from enum import Enum

@strawberry.enum
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

@strawberry.type
class User:
    id: strawberry.ID
    email: str
    name: str
    role: UserRole
    created_at: datetime
    posts: List["Post"] = strawberry.field(resolver=lambda self, info: get_user_posts(self.id, info))

@strawberry.type
class Post:
    id: strawberry.ID
    title: str
    content: str
    published: bool
    author_id: strawberry.ID
    created_at: datetime
    tags: List[str]

@strawberry.input
class CreatePostInput:
    title: str
    content: str
    tags: List[str] = strawberry.field(default_factory=list)

@strawberry.input
class UpdatePostInput:
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

@strawberry.type
class PostConnection:
    """Pagination with cursor-based pagination."""
    edges: List["PostEdge"]
    page_info: "PageInfo"
    total_count: int

@strawberry.type
class PostEdge:
    node: Post
    cursor: str

@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]
```

## Resolvers with Context

```python
from strawberry.types import Info
from dataclasses import dataclass
from functools import cached_property

@dataclass
class Context:
    db: AsyncSession
    current_user: Optional[User]
    request: Request

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: strawberry.ID, info: Info[Context, None]) -> Optional[User]:
        ctx = info.context
        # Authorization check
        if ctx.current_user is None:
            raise strawberry.PermissionError("Authentication required")

        result = await ctx.db.execute(
            select(UserModel).where(UserModel.id == id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return User.from_orm(user)

    @strawberry.field
    async def posts(
        self,
        info: Info[Context, None],
        first: int = 10,
        after: Optional[str] = None,
        search: Optional[str] = None,
        published_only: bool = True,
    ) -> PostConnection:
        ctx = info.context
        query = select(PostModel)

        if published_only:
            query = query.where(PostModel.published == True)

        if search:
            query = query.where(PostModel.title.ilike(f"%{search}%"))

        if after:
            cursor_id = decode_cursor(after)
            query = query.where(PostModel.id > cursor_id)

        # Get total count
        count_result = await ctx.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar()

        # Get page
        query = query.order_by(PostModel.created_at.desc()).limit(first + 1)
        result = await ctx.db.execute(query)
        posts = result.scalars().all()

        has_next = len(posts) > first
        posts = posts[:first]

        edges = [PostEdge(node=Post.from_orm(p), cursor=encode_cursor(p.id)) for p in posts]

        return PostConnection(
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next,
                has_previous_page=after is not None,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None,
            ),
            total_count=total,
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_post(
        self, input: CreatePostInput, info: Info[Context, None]
    ) -> Post:
        ctx = info.context
        if ctx.current_user is None:
            raise strawberry.PermissionError("Authentication required")

        post = PostModel(
            title=input.title,
            content=input.content,
            tags=input.tags,
            author_id=ctx.current_user.id,
        )
        ctx.db.add(post)
        await ctx.db.commit()
        await ctx.db.refresh(post)
        return Post.from_orm(post)

    @strawberry.mutation
    async def update_post(
        self, id: strawberry.ID, input: UpdatePostInput, info: Info[Context, None]
    ) -> Post:
        ctx = info.context
        result = await ctx.db.execute(select(PostModel).where(PostModel.id == id))
        post = result.scalar_one_or_none()

        if post is None:
            raise ValueError(f"Post {id} not found")

        if str(post.author_id) != str(ctx.current_user.id):
            raise strawberry.PermissionError("Not authorized to edit this post")

        if input.title is not None:
            post.title = input.title
        if input.content is not None:
            post.content = input.content
        if input.published is not None:
            post.published = input.published

        await ctx.db.commit()
        return Post.from_orm(post)
```

## DataLoaders (N+1 Prevention)

```python
from strawberry.dataloader import DataLoader
from typing import Sequence

# DataLoader for batching author lookups
async def load_users(keys: list[int]) -> list[Optional[User]]:
    """Batch load users by IDs."""
    async with get_db() as db:
        result = await db.execute(
            select(UserModel).where(UserModel.id.in_(keys))
        )
        users = {u.id: User.from_orm(u) for u in result.scalars().all()}
        return [users.get(key) for key in keys]

async def load_post_counts(user_ids: list[int]) -> list[int]:
    """Batch load post counts per user."""
    async with get_db() as db:
        result = await db.execute(
            select(PostModel.author_id, func.count(PostModel.id))
            .where(PostModel.author_id.in_(user_ids))
            .group_by(PostModel.author_id)
        )
        counts = dict(result.all())
        return [counts.get(uid, 0) for uid in user_ids]

# Context with DataLoaders
@dataclass
class Context:
    db: AsyncSession
    current_user: Optional[User]

    @cached_property
    def user_loader(self) -> DataLoader:
        return DataLoader(load_fn=load_users)

    @cached_property
    def post_count_loader(self) -> DataLoader:
        return DataLoader(load_fn=load_post_counts)

# Use in resolvers - batches automatically!
@strawberry.type
class Post:
    author_id: strawberry.ID

    @strawberry.field
    async def author(self, info: Info[Context, None]) -> Optional[User]:
        return await info.context.user_loader.load(int(self.author_id))
```

## Subscriptions

```python
import asyncio
from typing import AsyncGenerator

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def post_created(
        self, info: Info[Context, None]
    ) -> AsyncGenerator[Post, None]:
        """Subscribe to new post creation events."""
        channel = info.context.pubsub.subscribe("post:created")
        async with channel as messages:
            async for message in messages:
                post_data = json.loads(message)
                yield Post(**post_data)

    @strawberry.subscription
    async def post_updated(
        self, id: strawberry.ID, info: Info[Context, None]
    ) -> AsyncGenerator[Post, None]:
        """Subscribe to updates for a specific post."""
        channel = info.context.pubsub.subscribe(f"post:updated:{id}")
        async with channel as messages:
            async for message in messages:
                yield Post(**json.loads(message))

# Publish events from mutations
async def create_post_and_notify(input: CreatePostInput, ctx: Context) -> Post:
    post = await create_post(input, ctx)
    await ctx.pubsub.publish("post:created", post.to_json())
    return post

# Schema with subscriptions
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
```

## Permissions & Authentication

```python
from strawberry.permission import BasePermission

class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source, info: Info[Context, None], **kwargs) -> bool:
        return info.context.current_user is not None

class IsAdmin(BasePermission):
    message = "Admin access required"

    def has_permission(self, source, info: Info[Context, None], **kwargs) -> bool:
        user = info.context.current_user
        return user is not None and user.role == UserRole.ADMIN

class IsOwner(BasePermission):
    message = "You don't own this resource"

    def has_permission(self, source: Post, info: Info[Context, None], **kwargs) -> bool:
        return str(source.author_id) == str(info.context.current_user.id)

# Apply permissions
@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def me(self, info: Info[Context, None]) -> User:
        return info.context.current_user

    @strawberry.field(permission_classes=[IsAdmin])
    async def all_users(self, info: Info[Context, None]) -> List[User]:
        ...

# FastAPI context factory
from fastapi import Depends, Request

async def get_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Context:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    current_user = await verify_token(token) if token else None
    return Context(db=db, current_user=current_user)

graphql_router = GraphQLRouter(schema, context_getter=get_context)
```

## Key Patterns

- **DataLoaders** are mandatory — without them, N+1 queries will destroy performance
- **Cursor-based pagination** over offset — stable under concurrent inserts/deletes
- **Permission classes** centralize auth logic rather than repeating in every resolver
- **`Info[Context, None]`** typed context provides full IDE autocomplete
- **Subscriptions** need a pub/sub backend (Redis, channels) for multi-instance deployments
- **Query complexity limiting** prevents expensive queries: `schema = strawberry.Schema(..., extensions=[QueryDepthLimiter(max_depth=5)])`

## Models to Use

- **claude-opus-4-5**: Complex schema design, federation setup, subscription architecture
- **claude-sonnet-4-5**: Resolver implementation, DataLoader patterns, permission systems
- **claude-haiku-3-5**: Simple type additions, query writing, mutation inputs
