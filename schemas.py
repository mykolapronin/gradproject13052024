from datetime import datetime

from pydantic import BaseModel, HttpUrl, Field


class TourPrice(BaseModel):
    price: float = Field(gt=0, le=10_000, examples=[125.15])


class NewTour(TourPrice):
    title: str
    description: str
    cover: HttpUrl


class SavedTour(NewTour):
    id: int
    created_at: datetime


class DeletedTour(BaseModel):
    id: int
    deleted: bool = True
