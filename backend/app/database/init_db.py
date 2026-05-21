"""Initialize Beanie ODM with Motor."""
from __future__ import annotations

import logging

from beanie import init_beanie

from app.database.mongodb import get_database
from app.models import Project, Shot

logger = logging.getLogger(__name__)


async def init_db() -> None:
    db = get_database()
    await init_beanie(database=db, document_models=[Project, Shot])
    logger.info("Beanie initialized on database %s", db.name)
