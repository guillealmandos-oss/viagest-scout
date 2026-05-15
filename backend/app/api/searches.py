import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import UserFacingError
from app.core.i18n import AppLocale, get_request_locale, t
from app.schemas.common import SearchCreateRequest, SearchResponse
from app.schemas.searches import SearchListResponse
from app.services.orchestrator import SearchOrchestrator


router = APIRouter(prefix="/api/v1/searches", tags=["searches"])
service = SearchOrchestrator()
logger = logging.getLogger(__name__)


@router.get("", response_model=SearchListResponse)
def list_searches(
    db: Session = Depends(get_db),
    locale: AppLocale = Depends(get_request_locale),
) -> SearchListResponse:
    return service.list_searches(db, locale)


@router.post("", response_model=SearchResponse, status_code=status.HTTP_201_CREATED)
async def create_search(
    payload: SearchCreateRequest,
    db: Session = Depends(get_db),
    locale: AppLocale = Depends(get_request_locale),
) -> SearchResponse:
    try:
        return await service.execute_search(db, payload, locale)
    except UserFacingError as exc:
        raise HTTPException(status_code=exc.status_code, detail=t(locale, exc.message_key, **exc.params)) from exc
    except Exception:
        logger.exception("create_search failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=t(locale, "error.internal_server_error"),
        ) from None


@router.get("/{search_id}", response_model=SearchResponse)
def get_search(
    search_id: str,
    db: Session = Depends(get_db),
    locale: AppLocale = Depends(get_request_locale),
) -> SearchResponse:
    search = service.get_search(db, search_id, locale)
    if search is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t(locale, "error.search_not_found"))
    return search
