from fastapi import APIRouter

from ..schemas.ecosystem import CreateEcoSystem

router = APIRouter(prefix="/ecosystem", tags=["EcoSystem"])


@router.post("/")
async def create_ecosystem(eco_system: CreateEcoSystem):
    print(eco_system)
