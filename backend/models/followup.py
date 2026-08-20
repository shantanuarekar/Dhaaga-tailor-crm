from pydantic import BaseModel


class UpdateFollowupRequest(BaseModel):
    status: str
