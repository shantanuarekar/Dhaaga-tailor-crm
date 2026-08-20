from pydantic import BaseModel


class NewOrderRequest(BaseModel):
    customer_id: int
    garment_type: str
    price: float | str
    delivery_date: str | None = None
    fabric_photo_url: str | None = None


class UpdateOrderStatusRequest(BaseModel):
    status: str
