from fastapi import APIRouter

from app.api.dependencies import EcoSystemServiceDep
from app.api.schemas.organism import UpdateEcosystemOrganism
from app.api.utils.utils import verify_uuid

from ..schemas.ecosystem import CreateEcoSystem, UpdateEcoSystem

router = APIRouter(prefix="/ecosystem", tags=["ecosystem"])


@router.get("/{ecosystem_name_or_id}")
async def get_all_ecosystem_organisms(
    ecosystem_name_or_id: str, service: EcoSystemServiceDep
):
    return await service.get_all_ecosystem_organisms(ecosystem_name_or_id)


@router.get("/{ecosystem_id}/simulate")
async def simulate(ecosystem_id: str, service: EcoSystemServiceDep):
    return await service.simulate(verify_uuid(ecosystem_id))


@router.post("/create")
async def create_eco_system(ecosystem: CreateEcoSystem, service: EcoSystemServiceDep):
    return await service.add(ecosystem)


@router.post("/organism/add")
async def add_organism_to_a_eco_system(
    organism_name: str, ecosystem_id: str, service: EcoSystemServiceDep
):
    return await service.add_organism_to_a_eco_system(
        verify_uuid(ecosystem_id), organism_name
    )


@router.post("/plant/add")
async def add_plant_to_a_eco_system(
    plant_name: str, ecosystem_id: str, service: EcoSystemServiceDep
):
    return await service.add_plant_to_a_ecosystem(verify_uuid(ecosystem_id), plant_name)


@router.patch("/{organism_name}/update")
async def update_ecosystem_organism(
    ecosystem_id: str,
    updated_organism: UpdateEcosystemOrganism,
    service: EcoSystemServiceDep,
    organism_name: str,
):
    return await service.update_ecosystem_organism(
        verify_uuid(ecosystem_id), organism_name, updated_organism
    )


@router.patch("/{ecosystem_id}")
async def update_ecosystem_infos(
    ecosystem_id: str, update_infos: UpdateEcoSystem, service: EcoSystemServiceDep
):
    return await service.update_ecosystem(verify_uuid(ecosystem_id), update_infos)


@router.delete("/{ecosystem_id}")
async def delete_ecosystem(ecosystem_id: str, service: EcoSystemServiceDep):
    return await service.delete(verify_uuid(ecosystem_id))


@router.delete("/{ecosystem_id}/{organism_name_or_id}/remove")
async def remove_organism_from_a_ecosystem(
    ecosystem_id: str, organism_name_or_id: str, service: EcoSystemServiceDep
):
    return await service.remove_organism_from_a_ecosystem(
        verify_uuid(ecosystem_id), organism_name_or_id
    )
