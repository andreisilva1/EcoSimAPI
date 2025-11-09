from uuid import UUID

from pydantic import BaseModel


class BaseEcoSystem(BaseModel):
    name: str
    water_available: float
    minimum_water_to_add_per_simulation: int
    max_water_to_add_per_simulation: int


class AddOrganismToEcoSystem(BaseModel):
    eco_system_id: UUID
    organism_name: str


class CreateEcoSystem(BaseEcoSystem):
    pass


class UpdateEcoSystem(BaseEcoSystem):
    pass
