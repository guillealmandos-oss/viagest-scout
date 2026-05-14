from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import SearchResponse


class SearchSummaryItem(BaseModel):
    search_id: str
    origin: str
    destination: str
    provider_name: str
    created_at: datetime
    summary: str


class SearchListResponse(BaseModel):
    items: list[SearchSummaryItem]


class SearchDetailResponse(SearchResponse):
    pass
