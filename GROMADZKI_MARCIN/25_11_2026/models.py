from typing import Literal
from pydantic import BaseModel, Field, field_validator


class OrderCreateRequest(BaseModel):
    vehicle_id: int = Field(..., gt=0, description="ID of the vehicle")
    mechanic_id: int = Field(..., gt=0, description="ID of the assigned active mechanic")
    description: str = Field(..., min_length=1, description="Description of the reported issue")

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("description must not be empty or whitespace only.")
        return cleaned


class OrderServiceCreateRequest(BaseModel):
    service_id: int = Field(..., gt=0, description="ID of the service")
    hours_worked: float = Field(..., gt=0, description="Hours worked (must be > 0)")
    final_price: float = Field(..., ge=0, description="Total price for this service line (>= 0)")


class OrderServiceLineResponse(BaseModel):
    service_id: int
    service_name: str
    hours_worked: float
    final_price: float


class OrderDetailsResponse(BaseModel):
    id: int
    vehicle_id: int
    mechanic_id: int
    received_at: str
    completed_at: str | None = None
    status: Literal["received", "in_progress", "completed", "cancelled"]
    description: str
    total_price: float
    services: list[OrderServiceLineResponse]