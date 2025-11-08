from fastapi import APIRouter

from app.api.dependencies import EcoSystemServiceDep
from app.api.schemas.organism import UpdateEcosystemOrganism
from app.api.utils.utils import verify_uuid

from ..schemas.ecosystem import AddOrganismToEcoSystem, CreateEcoSystem

router = APIRouter(prefix="/ecosystem", tags=["ecosystem"])


@router.get("/{ecosystem_id}/simulate")
async def simulate(ecosystem_id: str, service: EcoSystemServiceDep):
    return await service.simulate(verify_uuid(ecosystem_id))


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
    return await service.update_ecosystem_organism(
        verify_uuid(ecosystem_id), organism_name, updated_organism
    )


@router.delete("/{ecosystem_id}")
async def delete_ecosystem(ecosystem_id: str, service: EcoSystemServiceDep):
    return await service.delete(verify_uuid(ecosystem_id))
