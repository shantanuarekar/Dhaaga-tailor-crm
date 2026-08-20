from pydantic import BaseModel


class NewPaymentRequest(BaseModel):
    amount: float | str
    type: str
    method: str | None = None
