from typing import List, Optional

from pydantic import BaseModel


class BusinessBase(BaseModel):
    id: int
    timezone: str
    rating: float
    max_rating: float
    review_count: int

    class Config:
        from_attributes = True


class BusinessHoursBase(BaseModel):
    id: int
    day: str
    shift1_start: Optional[str] = None
    shift1_end: Optional[str] = None
    shift2_start: Optional[str] = None
    shift2_end: Optional[str] = None

    class Config:
        from_attributes = True  # Ensure this is included


class CategoryBase(BaseModel):
    id: int
    category: str

    class Config:
        from_attributes = True


class BusinessResponse(BusinessBase):
    categories: List[CategoryBase] = []
    hours: List[BusinessHoursBase] = []

    class Config:
        from_attributes = True
