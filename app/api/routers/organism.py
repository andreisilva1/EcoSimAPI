from typing import Optional
from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies import OrganismServiceDep
from app.api.schemas.organism import (
    CreateOrganism,
    UpdateOrganism,
)
from app.api.utils.utils import verify_uuid
from app.database.enums import (
    ActivityCycle,
    DietType,
    OrganismType,
    SocialBehavior,
    Speed,
)

router = APIRouter(prefix="/organism", tags=["Organism"])


@router.post("/defaults")
async def filled_with_default_organisms(service: OrganismServiceDep):
    return await service.add_default()


@router.get("/")
async def get_organisms_by_name(search: str, service: OrganismServiceDep):
    return await service.get_multiple_organisms_by_name(search)


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


@router.patch("/{organism_id}/update")
async def update_organism(
    organism_id: UUID, update_infos: UpdateOrganism, service: OrganismServiceDep
):
    return await service.update_base_organism(organism_id, update_infos)


@router.delete("/{organism_id}/delete")
async def delete_organism(organism_id: str, service: OrganismServiceDep):
    return await service.delete(verify_uuid(organism_id))
