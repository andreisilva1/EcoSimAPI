from typing import Optional

from pydantic import BaseModel


class BasePlant(BaseModel):
    name: str
    weight: Optional[float] = None
    size: Optional[float] = None
    age: int = 0
    max_age: Optional[int] = None
    reproduction_age: Optional[int] = None
    fertility_rate: Optional[int] = None
    population: int = 1
    water_need: Optional[float] = None
    pollinators: Optional[str] = None


class CreatePlant(BasePlant):
    pass


class UpdatePlant(BasePlant):
    pass
