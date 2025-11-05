from fastapi import APIRouter

from app.api.dependencies import EcoSystemServiceDep

from ..schemas.ecosystem import CreateEcoSystem

router = APIRouter(prefix="/ecosystem", tags=["EcoSystem"])


@router.post("/")
async def create_ecosystem(eco_system: CreateEcoSystem, service: EcoSystemServiceDep):
    return await service.add(eco_system)
