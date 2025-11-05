from fastapi import APIRouter

from app.api.dependencies import EcoSystemServiceDep

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
