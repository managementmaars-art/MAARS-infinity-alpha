"""
FastAPI Project Template
A production-ready FastAPI application with best practices.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from typing import Annotated

from .config import settings
from .database import create_db_and_tables, get_session, Session
from .models import User, Item
from .auth import get_current_active_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    print("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    description="FastAPI application with best practices",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check(session: Annotated[Session, Depends(get_session)]):
    """Readiness check with database verification"""
    try:
        # Test database connection
        from sqlmodel import select
        session.exec(select(User).limit(1))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not available: {str(e)}")


# Example protected endpoint
@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Get current user information"""
    return current_user


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI",
        "docs": "/docs",
        "health": "/health"
    }
