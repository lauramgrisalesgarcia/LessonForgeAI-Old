from typing import Literal

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(..., description="Segundos hasta la expiración del token")
