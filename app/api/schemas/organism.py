from typing import Optional

from pydantic import BaseModel


class BaseOrganism(BaseModel):
    name: str
    weight: float
    size: float
    age: float = 0
    max_age: float
    reproduction_age: float
    fertility_rate: int = 1
    water_consumption: float
    food_consumption: float
    food_sources: Optional[str] = None
    predator: Optional[str] = None
    prey: Optional[str] = None
    weaknessMin: Optional[str] = None
    weaknessMax: Optional[str] = None
    pollination_target: Optional[str] = None
    territory_size: Optional[float] = None


class CreateOrganism(BaseOrganism):
    pass


class UpdateOrganism(BaseOrganism):
    name: str | None = None
    weight: float | None = None
    size: float | None = None
    age: float | None = None
    max_age: float | None = None
    reproduction_age: float | None = None
    fertility_rate: int | None = None
    water_consumption: float | None = None
    food_consumption: float | None = None
    food_sources: str | None = None
    predator: str | None = None
    prey: str | None = None
    weaknessMin: str | None = None
    weaknessMax: str | None = None
    pollination_target: str | None = None
    territory_size: float | None = None


class ReadOrganism(BaseOrganism):
    pass


class UpdateEcosystemOrganism(BaseModel):
    food_sources: Optional[str] = None
    predator: Optional[str] = None
    prey: Optional[str] = None
    weaknessMin: Optional[str] = None
    weaknessMax: Optional[str] = None
    pollination_target: Optional[str] = None
