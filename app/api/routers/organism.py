from typing import Optional
from uuid import UUID

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


@router.post("/")
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
