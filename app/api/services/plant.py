from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.plant import CreatePlant
from app.database.enums import PlantType
from app.database.models import Plant


class PlantService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, plant: CreatePlant, type: PlantType):
        new_plant = Plant(
            id=uuid4(),
            **plant.model_dump(exclude=["pollinators"]),
            type=type,
        )
        self.session.add(new_plant)
        await self.session.commit()
        return JSONResponse(
            status_code=201, content=jsonable_encoder({"created_plant": new_plant})
        )
