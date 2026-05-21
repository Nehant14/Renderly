from __future__ import annotations

from beanie.odm.fields import PydanticObjectId
from fastapi import HTTPException


def parse_object_id(raw: str, *, name: str = "id") -> PydanticObjectId:
    try:
        return PydanticObjectId(str(raw))
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Invalid {name}") from exc
