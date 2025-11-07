from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import EcoSystemServiceDep
from app.api.schemas.organism import UpdateEcosystemOrganism

from ..schemas.ecosystem import AddOrganismToEcoSystem, CreateEcoSystem

router = APIRouter(prefix="/ecosystem", tags=["ecosystem"])


@router.post("/")
async def create_eco_system(ecosystem: CreateEcoSystem, service: EcoSystemServiceDep):
    return await service.add(ecosystem)


@router.post("/add_organism_to_a_eco_system")
async def add_organism_to_a_eco_system(
    organism_and_eco_system: AddOrganismToEcoSystem, service: EcoSystemServiceDep
):
    return await service.add_organism_to_a_eco_system(organism_and_eco_system)


@router.patch("/{organism_name}")
async def update_ecosystem_organism(
    ecosystem_id: str,
    updated_organism: UpdateEcosystemOrganism,
    service: EcoSystemServiceDep,
    organism_name: str,
):
    if type(UUID(ecosystem_id)) is UUID:
        return await service.update_ecosystem_organism(
            UUID(ecosystem_id), organism_name, updated_organism
        )


@router.get("/{ecosystem_id}/simulate")
async def simulate(ecosystem_id: str, service: EcoSystemServiceDep):
    if type(UUID(ecosystem_id)) is UUID:
        return await service.simulate(UUID(ecosystem_id))
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide a real UUID."
    )
