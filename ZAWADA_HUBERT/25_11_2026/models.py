from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class OrderCreateRequest(BaseModel):
    vehicle_id: int = Field(..., gt=0, description="ID of the vehicle being serviced.")
    mechanic_id: int = Field(..., gt=0, description="ID of the assigned mechanic.")
    description: str = Field(..., min_length=1, description="Description of the repair order.")

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("description must not be empty or whitespace.")
        return stripped


class OrderServiceAddRequest(BaseModel):
    service_id: int = Field(..., gt=0, description="ID of the service performed.")
    hours_worked: float = Field(
        ..., gt=0, allow_inf_nan=False, description="Hours worked (must be > 0)."
    )
    final_price: float = Field(
        ..., ge=0, allow_inf_nan=False, description="Total price for this service line (must be >= 0)."
    )


class OrderServiceLineResponse(BaseModel):
    service_id: int
    service_name: str
    hours_worked: float
    final_price: float


class OrderResponse(BaseModel):
    id: int
    vehicle_id: int
    mechanic_id: int
    received_at: str
    completed_at: Optional[str] = None
    status: str
    description: str
    services: List[OrderServiceLineResponse] = Field(default_factory=list)
    total_price: float = 0.0