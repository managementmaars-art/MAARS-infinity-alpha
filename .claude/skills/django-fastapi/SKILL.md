---
name: django-fastapi
description: Django REST Framework and FastAPI — models, serializers, views, middleware, async endpoints, dependency injection, background tasks for MAARS Python web agents
---

# Django & FastAPI — MAARS Reference

## FastAPI Best Practices
```python
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr, field_validator
from typing import Annotated

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()
    yield
    # Shutdown
    await database.disconnect()

app = FastAPI(title="MAARS API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    model_config = {"from_attributes": True}

# Dependency injection
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = verify_token(token)
    user = await User.get(id=payload["sub"])
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

# Endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, bg: BackgroundTasks):
    user = await User.create(**data.model_dump())
    bg.add_task(send_welcome_email, user.email)
    return user

@app.get("/users/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return current_user
```

## FastAPI Routers & Structure
```python
# app/routers/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

# main.py
from app.routers import users, posts, auth
app.include_router(users.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
```

## SQLAlchemy Async
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import select, func

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
    posts: Mapped[list["Post"]] = relationship(back_populates="author",
                                               lazy="selectin")

# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# Queries
async def get_users_with_post_count(db: AsyncSession):
    result = await db.execute(
        select(User, func.count(Post.id).label("post_count"))
        .outerjoin(Post).group_by(User.id)
        .order_by(func.count(Post.id).desc())
    )
    return result.all()
```

## Django REST Framework
```python
# models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE,
                                related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
                              choices=[("draft","Draft"),("published","Published")],
                              default="draft")
    
    class Meta:
        indexes = [models.Index(fields=["author", "-created_at"])]
        ordering = ["-created_at"]

# serializers.py
from rest_framework import serializers

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    
    class Meta:
        model = Post
        fields = ["id", "title", "content", "author_name", "created_at", "status"]
        read_only_fields = ["id", "created_at"]
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title too short")
        return value

# views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "author"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "title"]
    
    def get_queryset(self):
        return Post.objects.select_related("author").all()
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# urls.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("posts", PostViewSet)
urlpatterns = [path("api/", include(router.urls))]
```

## Django Signals & Celery
```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    if created:
        send_welcome_email.delay(instance.email)  # Celery task

# tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, email: str):
    try:
        send_email(email, "Welcome!")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

## Models to Use
- **FastAPI code generation**: `claude-sonnet-4-6`
- **Django ORM queries**: `claude-sonnet-4-6`
- **API design**: `claude-opus-4-6`
