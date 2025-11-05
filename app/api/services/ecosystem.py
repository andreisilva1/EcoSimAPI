from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.ecosystem import CreateEcoSystem
from app.database.models import EcoSystem


class EcoSystemService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, eco_system: CreateEcoSystem):
        new_eco_system = EcoSystem(id=uuid4(), **eco_system.model_dump())
        self.session.add(new_eco_system)
        await self.session.commit()
        return new_eco_system
