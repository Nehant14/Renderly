import sys
import asyncio
import logging
from contextlib import asynccontextmanager

# Highlight: This must be executed at the absolute top of the file
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import get_settings
from app.database.init_db import init_db
from app.database.mongodb import close_client
from app.routes.health import router as health_router
from app.routes.projects import router as projects_router
from app.routes.shots import project_shots_router, router as shots_router
from app.utils.file_storage import storage_root

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("renderly.backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Highlight: Double check loop safety inside the dynamic worker thread lifespan
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
            
    await init_db()
    # Create storage root once, here
    storage_root().mkdir(parents=True, exist_ok=True)
    logger.info("Storage root: %s", storage_root())
    yield
    close_client()


app = FastAPI(title="Renderly API", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(shots_router, prefix="/api")
app.include_router(project_shots_router, prefix="/api")

# Mount static media — directory is guaranteed to exist from lifespan above
app.mount("/media", StaticFiles(directory=str(storage_root())), name="media")