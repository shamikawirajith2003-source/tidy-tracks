from typing import Literal, Optional

from pydantic import BaseModel, Field

EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(pattern=EMAIL, max_length=120)
    phone: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6, max_length=72)
    role: Literal["resident", "driver"]  # admin accounts cannot be self-registered
    stop: Optional[int] = Field(default=None, ge=1)
    vehicle: Optional[str] = Field(default=None, max_length=30)


class LoginIn(BaseModel):
    email: str = Field(max_length=120)
    password: str = Field(max_length=72)
    admin: bool = False


class PickupIn(BaseModel):
    material: Literal["Plastics", "Glass", "Paper", "E-waste"]
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class MessageIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: str = Field(pattern=EMAIL, max_length=120)
    message: str = Field(min_length=1, max_length=2000)


class IssueIn(BaseModel):
    kind: Literal["Blocked access", "Overloaded bin"]


class TruckIn(BaseModel):
    x: float = Field(ge=0, le=640)
    y: float = Field(ge=0, le=400)


class TrafficIn(BaseModel):
    slow: bool


class ActiveIn(BaseModel):
    active: bool


class ZoneIn(BaseModel):
    day: Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
