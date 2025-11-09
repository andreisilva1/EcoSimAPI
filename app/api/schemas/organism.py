from typing import Optional

from pydantic import BaseModel


class BaseOrganism(BaseModel):
    name: str
    weight: float
    size: float
    age: int = 0
    max_age: int
    reproduction_age: int
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
    pass


class ReadOrganism(BaseOrganism):
    pass


class UpdateEcosystemOrganism(BaseModel):
    food_sources: Optional[str] = None
    predator: Optional[str] = None
    prey: Optional[str] = None
    weaknessMin: Optional[str] = None
    weaknessMax: Optional[str] = None
    pollination_target: Optional[str] = None
