from typing import Optional

from fastapi import APIRouter

from app.api.dependencies import OrganismServiceDep
from app.api.schemas.organism import (
    CreateOrganism,
)
from app.database.enums import (
    ActivityCycle,
    DietType,
    OrganismType,
    SocialBehavior,
    Speed,
)

router = APIRouter(prefix="/organism", tags=["Organism"])


@router.post("/create")
async def create_organism(
    organism: CreateOrganism,
    type: OrganismType,
    diet_type: DietType,
    service: OrganismServiceDep,
    activity_cycle: Optional[ActivityCycle] = None,
    speed: Optional[Speed] = Speed.normal,
    social_behavior: Optional[SocialBehavior] = None,
):
    return await service.add(
        organism, type, diet_type, activity_cycle, speed, social_behavior
    )


@router.delete("/{organism_name_or_id}/delete")
async def delete_organism(organism_name_or_id: str, service: OrganismServiceDep):
    return await service.delete(organism_name_or_id)
