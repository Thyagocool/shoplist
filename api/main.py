from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from src.infrastructure.database.config import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)  # Just test the connection
    yield
    # Shutdown
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Shoplist API",
        description="API para gerenciamento de listas de compras",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static files for uploads
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    # TODO: Register routers here as features are implemented
    # app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    # app.include_router(category_router, prefix="/api/v1/categories", tags=["Categories"])
    # ...

    return app


app = create_app()
