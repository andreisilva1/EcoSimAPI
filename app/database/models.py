from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

from .enums import (
    ActivityCycle,
    DietType,
    OrganismType,
    PlantType,
    SocialBehavior,
    Speed,
)


class EcosystemOrganism(SQLModel, table=True):
    ecosystem_id: UUID = Field(foreign_key="ecosystem.id", primary_key=True)
    organism_id: UUID = Field(foreign_key="organism.id", primary_key=True)

    hunger: Optional[float] = Field(default=0.0)
    thirst: Optional[float] = Field(default=0.0)
    health: Optional[float] = Field(default=100.0)
    pregnant: Optional[bool] = Field(default=False)

    ecosystem: Optional["Ecosystem"] = Relationship(back_populates="organism_links")
    organism: Optional["Organism"] = Relationship(back_populates="ecosystem_links")


class PredationLink(SQLModel, table=True):
    predator_id: UUID = Field(foreign_key="organism.id", primary_key=True)
    prey_id: UUID = Field(foreign_key="organism.id", primary_key=True)


class PollinationLink(SQLModel, table=True):
    pollinator_id: UUID = Field(foreign_key="organism.id", primary_key=True)
    plant_id: UUID = Field(foreign_key="plant.id", primary_key=True)


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
    predator: List["Organism"] = Relationship(
        back_populates="prey",
        link_model=PredationLink,
        sa_relationship_kwargs={
            "primaryjoin": "Organism.id==PredationLink.predator_id",
            "secondaryjoin": "Organism.id==PredationLink.prey_id",
            "foreign_keys": "[PredationLink.predator_id, PredationLink.prey_id]",
        },
    )
    prey: List["Organism"] = Relationship(
        back_populates="predator",
        link_model=PredationLink,
        sa_relationship_kwargs={
            "primaryjoin": "Organism.id==PredationLink.prey_id",
            "secondaryjoin": "Organism.id==PredationLink.predator_id",
            "foreign_keys": "[PredationLink.predator_id, PredationLink.prey_id]",
        },
    )
    weaknessMin: Optional[str] = None
    weaknessMax: Optional[str] = None
    pollination_target: Optional[List["Plant"]] = Relationship(
        back_populates="pollinators", link_model=PollinationLink
    )

    # Behavior
    activity_cycle: Optional[ActivityCycle] = None  # day, night...
    speed: Optional[Speed] = Speed.normal
    territory_size: Optional[float] = None
    social_behavior: Optional[SocialBehavior] = None  # solitary, pack, herd

    ecosystem_links: List["EcosystemOrganism"] = Relationship(back_populates="organism")


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
        back_populates="pollination_target", link_model=PollinationLink
    )

    # Current state
    health: float = 100.0
    fruiting: bool = False

    # ecosystem relationship


class Ecosystem(SQLModel, table=True):
    id: UUID = Field(sa_column=Column(postgresql.UUID, index=True, primary_key=True))
    name: str

    water_available: float
    food_available: float = 0
    minimum_water_to_add_per_simulation: int
    max_water_to_add_per_simulation: int

    organism_links: List["EcosystemOrganism"] = Relationship(back_populates="ecosystem")
