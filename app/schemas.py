from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ============ Category System (Simplified - 3 Categories Only) ============

class CategoryBase(BaseModel):
    name: str  # EDIBLES, DRINKS, or NON-EDIBLES
    icon: Optional[str] = None
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# ============ Price (Enhanced with Item Details) ============

class PriceBase(BaseModel):
    category_id: int
    store_id: Optional[int] = None
    name: str  # Item name (required)
    brand: Optional[str] = None
    pack_size: Optional[str] = None
    pack_unit: Optional[str] = None
    price: float  # Price in ₦ (required)
    price_per_unit: Optional[float] = None
    retailer: Optional[str] = None
    location: Optional[str] = None

class PriceCreate(PriceBase):
    pass

class PriceOut(PriceBase):
    id: int
    submitted_by: Optional[int] = None
    submitted_at: datetime
    status: str

    class Config:
        from_attributes = True

# ============ Legacy (for backward compatibility) ============

class ItemBase(BaseModel):
    name: str
    category: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemOut(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ItemSubmissionCreate(BaseModel):
    name: str
    category: Optional[str] = None
    price: float
    location: str
    submitter_email: Optional[str] = None

class ItemSubmissionOut(BaseModel):
    id: int
    name: str
    category: Optional[str]
    price: float
    location: str
    status: str
    created_at: datetime

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

# Alias for backwards compatibility
PendingPriceResponse = PendingPriceOut
