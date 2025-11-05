from uuid import uuid4
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status
from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.ecosystem import AddOrganismToEcoSystem, CreateEcoSystem
from app.database.models import Ecosystem, Organism


class EcoSystemService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, eco_system_id: UUID):
        ecosystem = await self.session.get(
            Ecosystem, eco_system_id, options=[joinedload(Ecosystem.animals)]
        )
        return ecosystem

    async def add(self, ecosystem: CreateEcoSystem):
        new_eco_system = ecosystem(id=uuid4(), **ecosystem.model_dump())
        self.session.add(new_eco_system)
        await self.session.commit()
        return new_eco_system

    async def add_organism_to_a_eco_system(
        self, organism_and_eco_system: AddOrganismToEcoSystem
    ):
        organism_name, eco_system_id = (
            organism_and_eco_system.organism_name,
            organism_and_eco_system.eco_system_id,
        )

        ecosystem = await self.get(eco_system_id)
        if not ecosystem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No ecosystem found with the provided ID.",
            )
        organism_result = await self.session.execute(
            select(Organism).where(Organism.name == organism_name)
        )
        organism = organism_result.scalar_one_or_none()
        if organism and organism not in ecosystem.animals:
            ecosystem.animals.append(organism)
            organism.eco_system_id = ecosystem.id
            await self.session.commit()
            await self.session.refresh(ecosystem)

        return {"message": "ok"}
