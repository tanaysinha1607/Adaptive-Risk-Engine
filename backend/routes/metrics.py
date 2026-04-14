from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.services.metrics_service import get_metrics

router = APIRouter()


@router.get("")
def metrics(db: Session = Depends(get_db)) -> dict:
    return get_metrics(db)

