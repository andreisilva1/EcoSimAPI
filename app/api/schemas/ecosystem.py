# class EcoSystem(SQLModel, table=True):
#     id: UUID = Field(sa_column=Column(postgresql.UUID, index=True, primary_key=True))
#     name: str
#     animals: List["Organism"] = Relationship(
#         back_populates="ecosystem",
#         sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
#     )
#     plants: List["Plant"] = Relationship(
#         back_populates="ecosystem",
#         sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
#     )
#     water_available: float
#     food_available: float
#     minimum_water_to_add_per_simulation: int
#     max_water_to_add_per_simulation: int

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
