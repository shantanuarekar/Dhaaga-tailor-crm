from pydantic import BaseModel


class NewCustomerRequest(BaseModel):
    name: str
    phone: str
    referred_by: int | None = None


class MeasurementsRequest(BaseModel):
    chest: float | str | None = None
    waist: float | str | None = None
    hip: float | str | None = None
    shoulder: float | str | None = None
    sleeve_length: float | str | None = None
    length: float | str | None = None
    notes: str | None = None
    voice_note_url: str | None = None
