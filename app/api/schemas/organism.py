from typing import Optional

from pydantic import BaseModel

from app.database.enums import (
    ActivityCycle,
    DietType,
    OrganismType,
    SocialBehavior,
    Speed,
)


class BaseOrganism(BaseModel):
    name: str
    type: OrganismType
    weight: float
    size: float
    age: int = 0
    max_age: int
    reproduction_age: int
    fertility_age: int = 1
    water_consumption: float
    food_consumption: float
    diet_type: DietType
    food_sources: Optional[str] = None
    predators: Optional[str] = None
    preys: Optional[str] = None
    weaknessMin: Optional[str] = None
    weaknessMax: Optional[str] = None
    pollination_target: Optional[str] = None
    activity_cycle: Optional[ActivityCycle] = None
    speed: Optional[Speed] = Speed.normal
    territory_size: Optional[float] = None
    social_behavior: Optional[SocialBehavior] = None


class UpdateOrganism(BaseOrganism):
    pass


class ReadOrganism(BaseOrganism):
    pass
