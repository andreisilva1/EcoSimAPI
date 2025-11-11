from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.organism import CreateOrganism, UpdateOrganism
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

    async def get_multiple_organisms_by_name(self, organism_name: str):
        query = await self.session.scalars(
            select(Organism).where(
                func.lower(Organism.name).like(f"%{organism_name.lower()}%")
            )
        )

        organisms = query.all()
        if not organisms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No organism found with the name or ID provided.",
            )
        return organisms

    async def verify_if_organism_exists(self, organism_name):
        organism = await self.session.execute(
            select(Organism).where(Organism.name == organism_name)
        )
        return organism.scalar_one_or_none()

    async def get_organism_by_name_or_id(self, organism_name_or_id: str):
        try:
            valid_uuid = UUID(organism_name_or_id)
        except (ValueError, TypeError):
            valid_uuid = None
        finally:
            organism = await self.session.execute(
                select(Organism).where(
                    (Organism.name == organism_name_or_id or Organism.id == valid_uuid)
                    if valid_uuid
                    else Organism.name == organism_name_or_id
                )
            )
        organism = organism.scalar_one_or_none()
        if not organism:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No organism found with the name or ID provided.",
            )
        return organism

    async def add(
        self,
        create_organism: CreateOrganism,
        organism_type: OrganismType,
        diet_type: DietType,
        activity_cycle: Optional[ActivityCycle],
        speed: Optional[Speed],
        social_behavior: Optional[SocialBehavior],
    ):
        existent_organism = await self.verify_if_organism_exists(create_organism.name)
        if existent_organism:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A organism with this name already exists.",
            )
        predators_orm, preys_orm = [], []
        if create_organism.predator:
            predators_string = create_organism.predator.split(",")
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

        if create_organism.prey:
            preys_string = create_organism.prey.split(",")
            preys_orm = []
            if preys_string:
                for prey in preys_string:
                    organism = await self.session.execute(
                        select(Organism).where(
                            str(Organism.name).upper() == prey.upper()
                        )
                    )
                    if organism.scalar_one_or_none():
                        preys_orm.append(organism)

        new_organism = Organism(
            id=uuid4(),
            **create_organism.model_dump(
                exclude=["prey", "predator", "pollination_target", "ecosystem_links"]
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
        self, organism_name_or_id: str, update_organism: UpdateOrganism
    ):
        organism = await self.get_organism_by_name_or_id(organism_name_or_id)
        update = {}
        for key, value in update_organism.model_dump().items():
            if value is not None:
                update[key] = value
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No information to update has been provided.",
            )
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

    async def delete(self, organism_name_or_id: str):
        organism = await self.get_organism_by_name_or_id(organism_name_or_id)
        if not organism:
            try:
                organism = await self.session.get(Organism, UUID(organism_name_or_id))
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No organism found with the name or ID provided.",
                )
        if organism:
            await self.session.delete(organism)
            await self.session.commit()
            return Response(status_code=204)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organism found with the name or ID provided.",
        )
