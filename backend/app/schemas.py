from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["student", "educator", "institution_admin", "independent"]


class RegisterIn(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: Role = "independent"


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ActionOut(BaseModel):
    id: str
    label: str


class StepOut(BaseModel):
    id: str
    instruction: str
    hint: str = ""
    points: int


class SimulationSummary(BaseModel):
    id: str
    title: str
    area: str
    description: str
    step_count: int


class SimulationOut(BaseModel):
    id: str
    title: str
    area: str
    description: str
    actions: list[ActionOut]
    steps: list[StepOut]


class AttemptIn(BaseModel):
    simulation_id: str
    actions: list[str]
    duration_seconds: int = Field(default=0, ge=0)


class AttemptOut(BaseModel):
    id: int
    simulation_id: str
    score: int
    max_score: int
    duration_seconds: int
    errors: list[dict]
    created_at: datetime
