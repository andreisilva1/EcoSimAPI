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
    SimulationStatus,
    SocialBehavior,
    Speed,
)


class Simulation(SQLModel, table=True):
    simulation_id: UUID = Field(default_factory=uuid4, primary_key=True)
    ecosystem_id: UUID
    simulation_results: str


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
    age: float = 0
    max_age: float = 0
    reproduction_age: float = Field(ge=0, default=0)
    fertility_rate: int = 1

    # Needs
    water_consumption: float
    food_consumption: float
    diet_type: DietType  # carnivore, herbivore, omnivore, nectarivore

    # Interactions
    predator: Optional[List["Organism"]] = Relationship(
        back_populates="prey",
        link_model=PredationLink,
        sa_relationship_kwargs={
            "primaryjoin": lambda: Organism.id == PredationLink.prey_id,
            "secondaryjoin": lambda: Organism.id == PredationLink.predator_id,
            "foreign_keys": [PredationLink.prey_id, PredationLink.predator_id],
        },
    )
    prey: Optional[List["Organism"]] = Relationship(
        back_populates="predator",
        link_model=PredationLink,
        sa_relationship_kwargs={
            "primaryjoin": lambda: Organism.id == PredationLink.predator_id,
            "secondaryjoin": lambda: Organism.id == PredationLink.prey_id,
            "foreign_keys": [PredationLink.predator_id, PredationLink.prey_id],
        },
    )
    pollination_target: Optional[List["Plant"]] = Relationship(
        back_populates="pollinators",
        link_model=PollinationLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    # Behavior
    activity_cycle: Optional[ActivityCycle] = Field(
        default=ActivityCycle.diurnal
    )  # day, night...
    speed: Optional[Speed] = Field(default=Speed.normal)
    social_behavior: Optional[SocialBehavior] = Field(
        default=SocialBehavior.solitary
    )  # solitary, pack, herd

    ecosystem_id: UUID = Field(foreign_key="ecosystem.id", nullable=True)
    ecosystem: "Ecosystem" = Relationship(
        back_populates="organisms", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Uniques for each ecosystem they are added
    hunger: Optional[float] = Field(default=0.0)
    thirst: Optional[float] = Field(default=0.0)
    health: Optional[float] = Field(default=100.0)
    pregnant: Optional[bool] = Field(default=False)


class Plant(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    type: PlantType

    # Physical / Demography
    weight: Optional[float] = Field(default=0)  # biomass
    size: Optional[float] = Field(default=0)
    age: float = Field(ge=0, default=0)
    max_age: Optional[float] = Field(default=1)
    reproduction_age: Optional[float] = Field(default=0)
    fertility_rate: Optional[int] = Field(default=0)  # number of sements by cycle

    # Needs
    water_need: Optional[float] = Field(default=0)

    # Interactions
    pollinators: Optional[List["Organism"]] = Relationship(
        back_populates="pollination_target", link_model=PollinationLink
    )

    # Current state
    health: float = 100.0
    fruiting: bool = False

    ecosystem_id: UUID = Field(foreign_key="ecosystem.id", nullable=True)
    ecosystem: "Ecosystem" = Relationship(
        back_populates="plants", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Ecosystem(SQLModel, table=True):
    id: UUID = Field(sa_column=Column(postgresql.UUID, index=True, primary_key=True))
    name: str = Field(unique=True)

    water_available: float
    food_available: float = 0
    minimum_water_to_add_per_simulation: int
    max_water_to_add_per_simulation: int
    cycle: ActivityCycle = Field(default=ActivityCycle.diurnal)
    days: int = Field(default=0)
    organisms: List[Organism] = Relationship(
        back_populates="ecosystem",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )

    plants: List[Plant] = Relationship(
        back_populates="ecosystem",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    year: Optional[int] = 0
    simulation_status: SimulationStatus = Field(default=SimulationStatus.finished)
