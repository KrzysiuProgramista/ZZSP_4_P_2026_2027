from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    vehicle_id: int = Field(..., gt=0)
    mechanic_id: int = Field(..., gt=0)
    description: str = Field(..., min_length=1)


class OrderCreatedResponse(BaseModel):
    id: int
    status: str


class AddServiceRequest(BaseModel):
    service_id: int = Field(..., gt=0)
    hours_worked: float = Field(..., gt=0)
    final_price: float = Field(..., ge=0)


class OrderServiceLineResponse(BaseModel):
    service_id: int
    service_name: str
    hours_worked: float
    final_price: float


class OrderDetailsResponse(BaseModel):
    id: int
    vehicle_id: int
    mechanic_id: int
    customer_name: str
    mechanic_name: str
    vehicle_brand: str
    vehicle_model: str
    registration_no: str
    received_at: str
    completed_at: str | None = None
    status: str
    description: str
    services: list[OrderServiceLineResponse]
    total_price: float


class MessageResponse(BaseModel):
    message: str