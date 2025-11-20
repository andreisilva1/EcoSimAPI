from fastapi import APIRouter

from app.api.dependencies import PlantServiceDep
from app.api.schemas.plant import CreatePlant, UpdatePlant
from app.database.enums import PlantType

router = APIRouter(prefix="/plant", tags=["Plants"])


@router.get("/")
async def get_plants_by_name(search: str, service: PlantServiceDep):
    return await service.get_multiple_plants_by_name(search)


@router.post("/create")
async def create_plant(plant: CreatePlant, type: PlantType, service: PlantServiceDep):
    return await service.add(plant, type)


@router.patch("/{plant_name_or_id}/update")
async def update_plant(
    update_plant: UpdatePlant, plant_name_or_id: str, service: PlantServiceDep
):
    return await service.update_base_plant(plant_name_or_id, update_plant)


@router.delete("/{plant_name_or_id}/delete")
async def delete_plant(plant_name_or_id: str, service: PlantServiceDep):
    return await service.delete(plant_name_or_id)
