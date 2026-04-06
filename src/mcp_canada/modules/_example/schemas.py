"""Pydantic v2 schemas for the example module."""

from pydantic import BaseModel


class EchoResponse(BaseModel):
    """Schema for the echo response data."""

    message: str
    lang: str
    echoed: bool = True
