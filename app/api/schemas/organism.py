# from typing import Optional

# from pydantic import BaseModel

# from app.database.enums import ActivityCycle, OrganismType, SocialBehavior, Speed


# class BaseOrganism(BaseModel): Future option of create new Organisms
#     name: str
#     type: OrganismType
#     weight: float
#     size: float
#     age: int
#     water_consumption: float
#     food_consumption: float
#     diet_type: float
#     weaknessMin: Optional[str] = None
#     weaknessMax: Optional[str] = None
#     food_sources: Optional[str] = None
#     activity_cycle: Optional[ActivityCycle] = None
#     speed: Optional[Speed] = Speed.Normal
#     territory_size: Optional[float] = None
#     social_behavior: Optional[SocialBehavior]


# class CreateOrganism(BaseOrganism):
#     pass


# class UpdateOrganism(BaseOrganism):
#     pass


# class Organism(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     name: str
#     type: OrganismType  # predator, herbivore, polinizator, etc.

#     # Physical / Demography
#     weight: float
#     size: float
#     age: int = 0
#     max_age: int
#     reproduction_age: int
#     fertility_rate: int = 1

#     # Needs
#     water_consumption: float
#     food_consumption: float
#     diet_type: DietType  # carnivore, herbivore, omnivore, nectarivore
#     food_sources: Optional[str] = None

#     # Interactions
#     predator: List["Organism"] = Relationship(
#         back_populates="prey",
#         link_model=PredationLink,
#         sa_relationship_kwargs={
#             "primaryjoin": "Organism.id==PredationLink.predator_id",
#             "secondaryjoin": "Organism.id==PredationLink.prey_id",
#             "foreign_keys": "[PredationLink.predator_id, PredationLink.prey_id]",
#         },
#     )
#     prey: List["Organism"] = Relationship(
#         back_populates="predator",
#         link_model=PredationLink,
#         sa_relationship_kwargs={
#             "primaryjoin": "Organism.id==PredationLink.prey_id",
#             "secondaryjoin": "Organism.id==PredationLink.predator_id",
#             "foreign_keys": "[PredationLink.predator_id, PredationLink.prey_id]",
#         },
#     )
#     weaknessMin: Optional[str] = None
#     weaknessMax: Optional[str] = None
#     pollination_target: Optional[List["Plant"]] = Relationship(
#         back_populates="pollinators", link_model=PollinationLink
#     )

#     # Behavior
#     activity_cycle: Optional[ActivityCycle] = None  # day, night...
#     speed: Optional[float] = None
#     territory_size: Optional[float] = None
#     social_behavior: Optional[SocialBehavior] = None  # solitary, pack, herd

#     # Actual State
#     hunger: float = 0.0
#     thirst: float = 0.0
#     health: float = 100.0
#     pregnant: bool = False

#     # ecosystem Relationship
#     ecosystem_id: Optional[UUID] = Field(default=None, foreign_key="ecosystem.id")
#     ecosystem: Optional["ecosystem"] = Relationship(
#         back_populates="animals", sa_relationship_kwargs={"lazy": "selectin"}
#     )
