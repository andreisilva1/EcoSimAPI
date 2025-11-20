from uuid import UUID, uuid4

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exceptions.exceptions import (
    POLLINATORS_NOT_FOUND,
    RESOURCE_NAME_ALREADY_EXISTS,
    RESOURCE_NAME_NOT_FOUND,
    RESOURCE_NAME_OR_ID_NOT_FOUND,
)
from app.api.schemas.plant import CreatePlant, UpdatePlant
from app.database.enums import PlantType
from app.database.models import Organism, Plant


class PlantService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_multiple_plants_by_name(self, plant_name: str):
        query = await self.session.scalars(
            select(Plant).where(func.lower(Plant.name).like(f"%{plant_name.lower()}%"))
        )

        plants = query.all()
        if not plants:
            raise RESOURCE_NAME_NOT_FOUND("plant")

        return JSONResponse(
            status_code=200, content=jsonable_encoder({"plants": plants})
        )

    async def get_plant_by_name_or_id(self, plant_name_or_id: str):
        try:
            valid_uuid = UUID(plant_name_or_id)
        except (ValueError, TypeError):
            valid_uuid = None
        finally:
            plant = await self.session.execute(
                select(Plant).where(
                    (Plant.name == plant_name_or_id or Plant.id == valid_uuid)
                    if valid_uuid
                    else Plant.name == plant_name_or_id
                )
            )
        plant = plant.scalar_one_or_none()
        if not plant:
            raise RESOURCE_NAME_OR_ID_NOT_FOUND("plant")
        return plant

    async def verify_if_pollinator_exists(self, pollinator_name: str):
        result = await self.session.execute(
            select(Organism).where(Organism.name == pollinator_name)
        )

        pollinators = result.scalars().all()
        if not pollinators:
            raise POLLINATORS_NOT_FOUND(pollinator_name)
        return pollinators

    async def get_pollinators_and_convert_to_organisms(self, pollinators: str):
        pollinators_splitted = (
            pollinators.split(",") if "," in pollinators else [pollinators]
        )
        pollinators_converted = []
        for pollinator in pollinators_splitted:
            organisms = await self.verify_if_pollinator_exists(pollinator)
            for organism in organisms:
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
            raise RESOURCE_NAME_ALREADY_EXISTS("plant")
        pollinators_converted = []
        if plant.pollinators:
            pollinators_converted = await self.get_pollinators_and_convert_to_organisms(
                plant.pollinators
            )

        new_plant = Plant(
            id=uuid4(),
            **plant.model_dump(exclude=["pollinators"]),
            type=type,
        )
        new_plant.pollinators.extend(
            [
                pol
                for pol in pollinators_converted
                if pol.id not in {p.id for p in new_plant.pollinators}
            ]
        )

        self.session.add(new_plant)
        await self.session.commit()
        return JSONResponse(
            status_code=201,
            content=jsonable_encoder(
                {
                    "plant_created": new_plant,
                }
            ),
        )

    async def update_base_plant(self, plant_name_or_id: str, update_plant: UpdatePlant):
        plant = await self.get_plant_by_name_or_id(plant_name_or_id)
        update_infos = {}
        for key, value in update_plant:
            if value:
                update_infos[key] = value
        if "name" in update_infos.keys():
            existent_plant = await self.verify_if_plant_exists(update_infos["name"])
            if existent_plant:
                raise RESOURCE_NAME_ALREADY_EXISTS("plant")
        for key, value in update_infos.items():
            if key == "pollinators":
                update_infos[
                    "pollinators"
                ] = await self.get_pollinators_and_convert_to_organisms(
                    update_infos["pollinators"]
                )
            setattr(plant, key, value)
        await self.session.commit()
        await self.session.refresh(plant)
        return JSONResponse(
            status_code=200, content=jsonable_encoder({"updated_plant": plant})
        )

    async def delete(self, plant_name_or_id: str):
        await self.session.delete(await self.get_plant_by_name_or_id(plant_name_or_id))
        await self.session.commit()
        return Response(status_code=204)
