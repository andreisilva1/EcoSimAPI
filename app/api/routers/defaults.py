from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import func, select

from app.api.dependencies import SessionDep
from app.api.exceptions.exceptions import ALL_DEFAULTS_ALREADY_EXISTS
from app.api.utils.defaults import return_defaults
from app.database.models import Organism, Plant

router = APIRouter(prefix="/defaults", tags=["Defaults"])


@router.post(
    "/add_defaults",
    summary="Adds 20 default organisms and 10 default plants to test the system immediately!",
)
async def add_default_organisms_and_plants(session: SessionDep):
    default_organisms, default_plants = return_defaults()
    entities = [default_organisms, default_plants]
    organisms_added = []
    organisms_already_exists = []
    plants_added = []
    plant_already_exists = []
    for list_entity in entities:
        for entity in list_entity:
            if type(entity) is Organism:
                organism = entity
                query = await session.execute(
                    select(Organism).where(
                        (func.lower(Organism.name) == organism.name.lower())
                        & (Organism.ecosystem_id.is_(None))
                    )
                )

                existent_organism = query.scalar_one_or_none()
                if not existent_organism:
                    organisms_added.append(organism.name)
                    session.add(organism)
                else:
                    organisms_already_exists.append(organism.name)
            if type(entity) is Plant:
                plant = entity
                query = await session.execute(
                    select(Plant).where(
                        (func.lower(Plant.name) == plant.name.lower())
                        & (Plant.ecosystem_id.is_(None))
                    )
                )

                existent_plant = query.scalar_one_or_none()
                if not existent_plant:
                    plants_added.append(plant.name)
                    session.add(plant)
                else:
                    plant_already_exists.append(plant.name)

    await session.commit()
    if not organisms_added and not plants_added:
        raise ALL_DEFAULTS_ALREADY_EXISTS("organisms and plants")

    return JSONResponse(
        status_code=200,
        content={
            "organisms added": f"{len(organisms_added)}: {organisms_added}",
            "plants added": f"{len(plants_added)}: {plants_added}",
            "organisms not added (already exists)": f"{len(organisms_already_exists)}: {organisms_already_exists}",
            "plants not added (already exists)": f"{len(plant_already_exists)}: {plant_already_exists}",
        },
    )
