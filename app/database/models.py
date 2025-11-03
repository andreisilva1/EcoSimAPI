from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

from app.database.enums import (
    ActivityCycle,
    DietType,
    OrganismType,
    PlantType,
    SocialBehavior,
)


class PredationLink(SQLModel, table=True):
    predator_id: UUID = Field(foreign_key="organism.id", primary_key=True)
    prey_id: UUID = Field(foreign_key="organism.id", primary_key=True)


class Organism(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    type: OrganismType  # predator, herbivore, polinizator, etc.

    # Physical / Demography
    weight: float
    size: float
    age: int = 0
    max_age: int
    reproduction_age: int
    fertility_rate: int = 1

    # Needs
    water_consumption: float
    food_consumption: float
    diet_type: DietType  # carnivore, herbivore, omnivore, nectarivore
    food_sources: Optional[str] = None

    # Interactions
    predators: List["Organism"] = Relationship(
        back_populates="prey", link_model=PredationLink
    )
    prey: List["Organism"] = Relationship(
        back_populates="predator", link_model=PredationLink
    )
    weaknessMin: Optional[str] = None
    weaknessMax: Optional[str] = None
    pollination_target: Optional[str] = None

    # Behavior
    activity_cycle: Optional[ActivityCycle] = None  # day, night...
    speed: Optional[float] = None
    territory_size: Optional[float] = None
    social_behavior: Optional[SocialBehavior] = None  # solitary, pack, herd

    # Actual State
    hunger: float = 0.0
    thirst: float = 0.0
    health: float = 100.0
    pregnant: bool = False

    # Ecosystem Relationship
    ecosystem_id: Optional[UUID] = Field(default=None, foreign_key="ecosystem.id")
    ecosystem: Optional["EcoSystem"] = Relationship(
        back_populates="animals", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Plant(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    type: PlantType

    # Physical / Demography
    weight: Optional[float] = None  # biomass
    size: Optional[float] = None
    age: int = 0
    max_age: Optional[int] = None
    reproduction_age: Optional[int] = None
    fertility_rate: Optional[int] = None  # number of sements by cycle
    population: int = 1

    # Needs
    water_need: Optional[float] = None
    sunlight_need: Optional[float] = None
    nutrient_need: Optional[float] = None

    # Interactions
    pollinators: Optional[List["Organism"]] = Relationship(
        back_populates="pollination_target"
    )
    consumed_by: Optional[List["Organism"]] = Relationship(
        back_populates="food_sources"
    )

    # Current state
    health: float = 100.0
    fruiting: bool = False

    # Ecosystem relationship
    ecosystem_id: Optional[UUID] = Field(default=None, foreign_key="ecosystem.id")
    ecosystem: Optional["EcoSystem"] = Relationship(back_populates="plants")


class EcoSystem(SQLModel, table=True):
    id: UUID = Field(sa_column=Column(postgresql.UUID, index=True, primary_key=True))
    name: str
    animals: List["Organism"] = Relationship(
        back_populates="ecosystem",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    plants: List["Plant"] = Relationship(
        back_populates="ecosystem",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    water_available: float
    food_available: float
    minimum_water_to_add_per_simulation: int
    max_water_to_add_per_simulation: int
