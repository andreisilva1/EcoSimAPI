from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.organism import CreateOrganism
from app.database.enums import (
    ActivityCycle,
    DietType,
    OrganismType,
    SocialBehavior,
    Speed,
)
from app.database.models import Organism, PredationLink


class OrganismService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        create_organism: CreateOrganism,
        organism_type: OrganismType,
        diet_type: DietType,
        activity_cycle: Optional[ActivityCycle],
        speed: Optional[Speed],
        social_behavior: Optional[SocialBehavior],
    ):
        predators_string = create_organism.predators.split(",")
        predators_orm = []
        if predators_string:
            for predator in predators_string:
                organism = await self.session.execute(
                    select(Organism).where(
                        str(Organism.name).upper() == predator.upper()
                    )
                )
                if organism.scalar_one_or_none():
                    predators_orm.append(organism)

        preys_string = create_organism.preys.split(",")
        preys_orm = []
        if preys_string:
            for prey in preys_string:
                organism = await self.session.execute(
                    select(Organism).where(str(Organism.name).upper() == prey.upper())
                )
                if organism.scalar_one_or_none():
                    preys_orm.append(organism)

        new_organism = Organism(
            id=uuid4(),
            **create_organism.model_dump(
                exclude=["preys", "predators", "pollination_target", "ecosystem_links"]
            ),
            type=OrganismType(organism_type),
            diet_type=DietType(diet_type),
            activity_cycle=ActivityCycle(activity_cycle)
            if activity_cycle
            else ActivityCycle.diurnal,
            speed=Speed(speed) if speed else Speed.normal,
            social_behavior=SocialBehavior(social_behavior)
            if social_behavior
            else SocialBehavior.pack,
        )

        for predator in predators_orm:
            new_relation = PredationLink(
                predator_id=predator.id, prey_id=new_organism.id
            )
            self.session.add(new_relation)

        for prey in preys_orm:
            new_relation = PredationLink(predator_id=new_organism.id, prey_id=prey.id)
            self.session.add(new_relation)
        self.session.add(new_organism)
        await self.session.commit()
        return new_organism
