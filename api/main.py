from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from src.infrastructure.database.config import engine
from src.presentation.api.errors.handlers import register_error_handlers
from src.presentation.api.routers.auth_router import router as auth_router
from src.presentation.api.routers.category_router import router as category_router
from src.presentation.api.routers.item_router import router as item_router
from src.presentation.api.routers.store_router import router as store_router
from src.presentation.api.routers.inventory_router import router as inventory_router
from src.presentation.api.routers.ocr_router import router as ocr_router
from src.presentation.api.routers.shopping_list_router import router as shopping_list_router
from src.presentation.api.routers.inventories_router import router as inventories_router
from src.presentation.api.routers.stock_router import router as stock_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)
    yield
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

    # Error handlers
    register_error_handlers(app)

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    # Routers
    app.include_router(auth_router)
    app.include_router(category_router)
    app.include_router(item_router)
    app.include_router(store_router)
    app.include_router(inventory_router)
    app.include_router(ocr_router)
    app.include_router(shopping_list_router)
    app.include_router(inventories_router)
    app.include_router(stock_router)

    return app


app = create_app()
