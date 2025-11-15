
from pydantic import BaseModel


class BaseEcoSystem(BaseModel):
    name: str
    water_available: float
    minimum_water_to_add_per_simulation: int
    max_water_to_add_per_simulation: int


class CreateEcoSystem(BaseEcoSystem):
    pass


class UpdateEcoSystem(BaseEcoSystem):
    pass
