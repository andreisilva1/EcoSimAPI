from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.plant import CreatePlant
from app.api.services.organism import OrganismService
from app.database.enums import PlantType
from app.database.models import Organism, Plant


class PlantService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def verify_if_pollinator_exists(self, pollinator_name: str):
        pollinator = await self.session.execute(
            select(Organism).where(Organism.name == pollinator_name)
        )
        pollinator = pollinator.scalar_one_or_none()
        if not pollinator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No organism with that name was found: ({pollinator_name}). You can delete it from the pollinators field or correct its name.",
            )
        return pollinator

    async def get_pollinators_and_convert_to_organisms(self, pollinators: str):
        pollinators_splitted = pollinators.split(",")
        pollinators_converted = []
        for pollinator in pollinators_splitted:
            organism = await self.verify_if_pollinator_exists(pollinator)
            pollinators_converted.append(organism)
        return pollinators_converted

    async def verify_if_plant_exists(self, plant_name: str):
        plant = await self.session.execute(
            select(Plant).where(Plant.name == plant_name)
        )
        plant = plant.scalar_one_or_none()
        return plant

    async def add(self, plant: CreatePlant, type: PlantType):
        existent_plant = await self.verify_if_plant_exists(plant.name)
        if existent_plant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A plant with this name already exists.",
            )
        pollinators_converted = []
        if plant.pollinators:
            pollinators_converted = await self.get_pollinators_and_convert_to_organisms(
                plant.pollinators
            )
        new_plant = Plant(
            id=uuid4(),
            **plant.model_dump(exclude=["pollinators"]),
            type=type,
            pollinators=pollinators_converted if pollinators_converted else [],
        )
        self.session.add(new_plant)
        await self.session.commit()
        return JSONResponse(
            status_code=201, content=jsonable_encoder({"created_plant": new_plant})
        )
