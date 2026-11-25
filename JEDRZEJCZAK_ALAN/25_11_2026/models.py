from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    vehicle_id: int = Field(gt=0)
    mechanic_id: int = Field(gt=0)
    description: str = Field(min_length=1)


class ServiceCreate(BaseModel):
    service_id: int = Field(gt=0)
    hours_worked: float = Field(gt=0, allow_inf_nan=False)
    final_price: float = Field(ge=0, allow_inf_nan=False)


class ServiceLine(BaseModel):
    service_id: int
    service_name: str
    hours_worked: float
    final_price: float


class OrderDetails(BaseModel):
    id: int
    vehicle_id: int
    mechanic_id: int
    received_at: str
    completed_at: str | None
    status: str
    description: str
    services: list[ServiceLine]
    total_price: float


class ServiceAdded(BaseModel):
    order_id: int
    service_id: int
    status: str


class OrderCompleted(BaseModel):
    order_id: int
    status: str
    completed_at: str
