from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.ecosystem import EcoSystemService
from app.database.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_ecosystem_service(session: SessionDep):
    return EcoSystemService(session)


EcoSystemServiceDep = Annotated[EcoSystemService, Depends(get_ecosystem_service)]
