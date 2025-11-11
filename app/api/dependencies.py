from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.ecosystem import EcoSystemService
from app.api.services.organism import OrganismService
from app.api.services.plant import PlantService
from app.database.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_ecosystem_service(session: SessionDep):
    return EcoSystemService(session)


def get_organism_service(session: SessionDep):
    return OrganismService(session)


def get_plant_service(session: SessionDep):
    return PlantService(session)


EcoSystemServiceDep = Annotated[EcoSystemService, Depends(get_ecosystem_service)]
OrganismServiceDep = Annotated[OrganismService, Depends(get_organism_service)]
PlantServiceDep = Annotated[PlantService, Depends(get_plant_service)]
