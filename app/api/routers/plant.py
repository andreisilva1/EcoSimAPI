from fastapi import APIRouter

from app.api.dependencies import PlantServiceDep
from app.api.schemas.plant import CreatePlant
from app.database.enums import PlantType

router = APIRouter(prefix="/plant", tags=["Plants"])


@router.post("/")
async def create_plant(plant: CreatePlant, type: PlantType, service: PlantServiceDep):
    return await service.add(plant, type)
