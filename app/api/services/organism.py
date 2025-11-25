from typing import Optional
from uuid import UUID, uuid4

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions.exceptions import (
    BLANK_UPDATE_FIELDS_ERROR,
    RESOURCE_ID_NOT_FOUND_ERROR,
    RESOURCE_NAME_ALREADY_EXISTS_ERROR,
    RESOURCE_NAME_NOT_FOUND_ERROR,
)
from app.api.schemas.organism import CreateOrganism, UpdateOrganism
from app.database.enums import (
    ActivityCycle,
    DietType,
    EnvironmentType,
    OrganismType,
    SocialBehavior,
    Speed,
)
from app.database.models import Organism, Plant, PollinationLink, PredationLink


class OrganismService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_organisms(self, detailed: bool):
        query = await self.session.scalars(select(Organism))
        organisms = query.all()
        if not detailed:
            organisms = [organism.name for organism in organisms]
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"organisms": organisms}),
        )

    async def get_multiple_organisms_by_name(self, organism_name: str):
        query = await self.session.scalars(
            select(Organism).where(
                func.lower(Organism.name).like(f"%{organism_name.lower()}%")
            )
        )

        organisms = query.all()
        if not organisms:
            raise RESOURCE_NAME_NOT_FOUND_ERROR("organism")
        return organisms

    async def verify_if_organism_exists(self, organism_name):
        organism = await self.session.execute(
            select(Organism).where(func.lower(Organism.name) == organism_name.lower())
        )
        return organism.scalar_one_or_none()

    async def get_organism_by_id(self, organism_id: UUID):
        organism = await self.session.execute(
            select(Organism).where((Organism.id == organism_id))
        )
        organism = organism.scalar_one_or_none()
        if not organism:
            raise RESOURCE_ID_NOT_FOUND_ERROR("organism")

        return organism

    async def add(
        self,
        create_organism: CreateOrganism,
        organism_type: OrganismType,
        diet_type: DietType,
        activity_cycle: Optional[ActivityCycle],
        speed: Optional[Speed],
        social_behavior: Optional[SocialBehavior],
        environment_type: EnvironmentType | None,
    ):
        existent_organism = await self.verify_if_organism_exists(create_organism.name)
        if existent_organism:
            raise RESOURCE_NAME_ALREADY_EXISTS_ERROR("organism")

        predators_orm, preys_orm = [], []
        if create_organism.predator:
            predators_string = (
                create_organism.predator.split(",")
                if "," in create_organism.predator
                else [create_organism.predator]
            )
            predators_orm = []
            if predators_string:
                for predator in predators_string:
                    query = await self.session.execute(
                        select(Organism).where(
                            (func.lower(Organism.name) == predator.lower())
                            & (Organism.ecosystem_id.is_(None))
                        )
                    )
                    organism = query.scalar_one_or_none()
                    if organism:
                        predators_orm.append(organism)

        if create_organism.prey:
            preys_string = (
                create_organism.prey.split(",")
                if "," in create_organism.prey
                else [create_organism.prey]
            )
            preys_orm = []
            if preys_string:
                for prey in preys_string:
                    query = await self.session.execute(
                        select(Organism).where(
                            func.lower(Organism.name) == prey.lower(),
                            Organism.ecosystem_id.is_(None),
                        )
                    )

                    organism = query.scalar_one_or_none()
                    if organism:
                        preys_orm.append(organism)
        pollination_target = (
            await self.get_pollination_targets_and_convert_to_organisms(
                str(create_organism.pollination_target)
            )
            if create_organism.pollination_target
            else []
        )
        new_organism = Organism(
            id=uuid4(),
            pollination_target=pollination_target,
            **create_organism.model_dump(
                exclude=["prey", "predator", "pollination_target"],
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
            environment_type=environment_type,
        )

        for target in pollination_target:
            new_pollination_link = PollinationLink(new_organism.id, target.id)
            self.session.add(new_pollination_link)
        if predators_orm:
            for predator in predators_orm:
                new_relation = PredationLink(
                    predator_id=predator.id, prey_id=new_organism.id
                )
                self.session.add(new_relation)

        if preys_orm:
            for prey in preys_orm:
                new_relation = PredationLink(
                    predator_id=new_organism.id, prey_id=prey.id
                )
                self.session.add(new_relation)
        self.session.add(new_organism)
        await self.session.commit()

        return JSONResponse(
            status_code=201,
            content=jsonable_encoder({"organism_created": new_organism}),
        )

    async def update_base_organism(
        self, organism_id: UUID, update_organism: UpdateOrganism
    ):
        organism = await self.get_organism_by_id(organism_id)
        update = {}
        for key, value in update_organism.model_dump().items():
            if value is not None:
                update[key] = value
        if not update:
            raise BLANK_UPDATE_FIELDS_ERROR()
        for key, value in update.items():
            try:
                setattr(organism, key, value)
            except TypeError:
                value = value.split(",")
                setattr(organism, key, value)
        await self.session.commit()
        await self.session.refresh(organism)
        return JSONResponse(
            status_code=200, content=jsonable_encoder({"updated_organism": organism})
        )

    async def delete(self, organism_id: UUID):
        organism = await self.get_organism_by_id(organism_id)
        if not organism:
            raise RESOURCE_ID_NOT_FOUND_ERROR("organism")

        await self.session.delete(organism)
        await self.session.commit()
        return Response(status_code=204)

    async def get_pollination_targets_and_convert_to_organisms(
        self, pollination_targets: str
    ):
        pollination_targets_splitted = pollination_targets.split(",")
        pollination_targets_converted = []
        for pollination_target in pollination_targets_splitted:
            pollination_target = await self.session.execute(
                select(Plant).where(
                    func.lower(Organism.name) == pollination_target.lower()
                )
            )
            pollination_target = pollination_target.scalar_one_or_none()
            if pollination_target:
                pollination_targets_converted.append(pollination_target)
        return pollination_targets_converted
