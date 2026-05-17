from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.habits import router as habits_router
from app.api.groups import router as groups_router
from app.api.messages import router as messages_router
from app.api.wellness import router as wellness_router
from app.api.analytics import router as analytics_router
from app.api.kpi import router as kpi_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: Initialize database
    await init_db()
    print("Database initialized successfully!")
    
    yield
    
    # Shutdown: Cleanup if needed
    print("Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A social health and wellness platform API",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(habits_router, prefix="/api/v1")
app.include_router(groups_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(wellness_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(kpi_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
