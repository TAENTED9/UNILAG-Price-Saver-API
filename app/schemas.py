from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PriceBase(BaseModel):
    item_id: int
    location: Optional[str] = None
    amount: float

class PriceCreate(PriceBase):
    pass

class PriceOut(PriceBase):
    id: int
    submitted_at: datetime

    class Config:
        from_attributes = True

class PendingPriceCreate(BaseModel):
    item: str
    parsed_price: Optional[float] = None
    location_text: Optional[str] = None
    submitter_email: Optional[str] = None

class PendingPriceOut(BaseModel):
    id: int
    item: str
    parsed_price: Optional[float]
    image_path: Optional[str]
    submitter_id: Optional[int]
    location_text: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class HeatmapLocation(BaseModel):
    key: str
    name: str
    store_id: Optional[int]
    lat: Optional[float]
    lng: Optional[float]
    count: int
    avg_price: float
    min_price: float
    max_price: float
    intensity: float

class HeatmapResponse(BaseModel):
    item: str
    days: int
    generated_at: datetime
    heatmap: List[HeatmapLocation]

    class Config:
        from_attributes = True

class CheapestLocation(BaseModel):
    price: float
    store: Optional[dict]
    submitted_at: datetime

class SearchResponse(BaseModel):
    item: str
    cheapest: Optional[CheapestLocation]
    top5: List[CheapestLocation]
    heatmap_path: Optional[str]
