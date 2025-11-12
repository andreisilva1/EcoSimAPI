import random
from typing import List
from uuid import UUID, uuid4

from fastapi import HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.ecosystem import (
    AddOrganismToEcoSystem,
    CreateEcoSystem,
    UpdateEcoSystem,
)
from app.api.schemas.organism import UpdateEcosystemOrganism
from app.api.utils.interaction_functions import (
    drink_water,
    graze_plants,
    hunt_prey,
    reproduce,
    rest,
)
from app.database.enums import ActivityCycle, OrganismType
from app.database.interactions_list import ACTIONS_BY_TYPE
from app.database.models import Ecosystem, Organism, Plant


class EcoSystemService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, ecosystem_id: UUID):
        ecosystem = await self.session.get(Ecosystem, ecosystem_id)
        if not ecosystem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No ecosystem found with the provided ID.",
            )
        return ecosystem

    async def get_all_ecosystem_organisms(self, ecosystem_name_or_id: str):
        try:
            valid_uuid = UUID(ecosystem_name_or_id)
        except (ValueError, TypeError):
            valid_uuid = None
            ecosystem = await self.session.execute(
                select(Ecosystem).where(
                    (
                        Ecosystem.name == ecosystem_name_or_id
                        or Ecosystem.id == valid_uuid
                    )
                    if valid_uuid
                    else Ecosystem.name == ecosystem_name_or_id
                )
            )
        ecosystem = ecosystem.scalar_one_or_none()
        if ecosystem:
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({"all_organisms": ecosystem.organisms}),
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No ecosystem found with the ID or name provided.",
        )

    async def add(self, ecosystem: CreateEcoSystem):
        new_eco_system = Ecosystem(id=uuid4(), **ecosystem.model_dump())
        self.session.add(new_eco_system)
        await self.session.commit()
        return JSONResponse(
            status_code=201,
            content=jsonable_encoder({"ecosystem_created": new_eco_system}),
        )

    async def update_ecosystem(
        self, ecosystem_id: UUID, update_ecosystem: UpdateEcoSystem
    ):
        ecosystem = await self.get(ecosystem_id)
        updates = {}
        for key, value in update_ecosystem.model_dump().items():
            if value:
                updates[key] = value
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update fields has been filled.",
            )
        for key, value in updates.items():
            setattr(ecosystem, key, value)
        await self.session.commit()
        await self.session.refresh(ecosystem)
        return JSONResponse(
            status_code=200, content=jsonable_encoder({"updated_ecosystem": ecosystem})
        )

    async def extract_organism_by_name(self, name: str):
        organism = await self.session.execute(
            select(Organism).where(Organism.name == name)
        )
        return organism.scalar_one_or_none()

    async def extract_organisms_from_a_specific_ecosystem_by_name(
        self, ecosystem_id: UUID, name: str
    ):
        ecosystem = await self.session.execute(
            select(Ecosystem).where(Ecosystem.id == ecosystem_id)
        )
        ecosystem = ecosystem.scalar_one_or_none()
        if ecosystem:
            organisms = [
                organism for organism in ecosystem.organisms if organism.name == name
            ]
        return organisms

    async def extract_plant_by_name(self, name: str):
        plant = await self.session.execute(select(Plant).where(Plant.name == name))
        return plant.scalar_one_or_none()

    async def convert_pollination_target_to_plant(
        self, pollination_target: str
    ) -> List[Plant]:
        pollination_target_splitted = pollination_target.split(",")
        targets = []
        for target in pollination_target_splitted:
            plant = await self.session.execute(
                select(Plant).where(Plant.name == target)
            )
            plant = plant.scalar_one_or_none()
            if plant:
                targets.append(plant)
        return targets

    async def add_organism_to_a_eco_system(
        self, organism_and_eco_system: AddOrganismToEcoSystem
    ):
        organism_name, eco_system_id = (
            organism_and_eco_system.organism_name,
            organism_and_eco_system.eco_system_id,
        )

        ecosystem = await self.get(eco_system_id)

        organism = await self.extract_organism_by_name(organism_name)

        if not organism:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No organism found with the provided name.",
            )

        new_organism_to_this_ecosystem = organism.model_copy()
        new_organism_to_this_ecosystem.id = uuid4()
        ecosystem.organisms.append(new_organism_to_this_ecosystem)
        await self.session.commit()
        return JSONResponse(
            status_code=201,
            content={
                "message": f"""{new_organism_to_this_ecosystem.name}
            added to the ecosystem {ecosystem.name}"""
            },
        )

    async def update_ecosystem_organism(
        self, ecosystem_id, organism_name, updated_organism: UpdateEcosystemOrganism
    ):
        ecosystem = await self.get(ecosystem_id)
        organism = await self.extract_organism_by_name(organism_name)
        if not ecosystem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The provided ecosystem doesn't exist.",
            )

        if not organism:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The provided organism doesn't exist in the ecosystem.",
            )

        updated_fields = {}
        for key, value in updated_organism.model_dump().items():
            if value:
                updated_fields[key] = value

        for field in updated_fields:
            entities_to_add = updated_fields[field].split(",")

            for entity in entities_to_add:
                if field != "pollination_target":
                    entities_in_the_ecosystem = (
                        await self.extract_organisms_from_a_specific_ecosystem_by_name(
                            ecosystem_id, entity
                        )
                    )
                # else:
                #     entity_in_database = await self.extract_plant_by_name(entity)

                if entities_in_the_ecosystem:
                    list_entities = getattr(organism, field)
                    for entity_in_the_ecosystem in entities_in_the_ecosystem:
                        list_entities.append(entity_in_the_ecosystem)
                    await self.session.commit()
        return JSONResponse(
            status_code=200, content={"message": f"Organism {organism_name} updated."}
        )

    async def simulate(self, ecosystem_id: UUID):
        ecosystem = await self.get(ecosystem_id)

        results = []
        organisms = ecosystem.organisms
        for organism in organisms:
            possible_interactions = ACTIONS_BY_TYPE[organism.type]
            action = random.choice(possible_interactions)
            if action == "rest":
                results.append(rest(organism))

            if action == "reproduce":
                organism_to_reproduce = await self.session.execute(
                    select(Organism).where(
                        Organism.name == organism.name,
                        Organism.id != organism.id,
                        Organism.pregnant.is_(False),
                    )
                )
                organism_to_reproduce = organism_to_reproduce.scalar_one_or_none()
                if organism_to_reproduce:
                    results.append(reproduce([organism, organism_to_reproduce]))
                else:
                    results.append({f"No partner has been found to {organism.name}."})

            if action == "drink_water":
                results.append(drink_water(ecosystem, organism))

            if organism.type == OrganismType.predator:
                if action == "hunt_prey":
                    results.append(hunt_prey(organism, organisms))

            elif organism.type == OrganismType.herbivore:
                if action == "graze_plants":
                    if not organism.pollination_target:
                        results.append({f"No pollinators found for {organism.name}"})
                    else:
                        pollination_target = random.choice(organism.pollination_target)
                        results.append(graze_plants(pollination_target, organism))

            elif organism.type == OrganismType.herbivore:
                if action == "find_food":
                    action = random.choice(["hunt_prey", "graze_plants"])
                    match action:
                        case "hunt_prey":
                            results.append(hunt_prey(organism, organisms))
                        case "graze_plants":
                            targets = await self.convert_pollination_target_to_plant(
                                organism.pollinators
                            )
                            if not targets:
                                results.append(
                                    {f"No pollinators found for {organism.name}"}
                                )
                            else:
                                results.append(graze_plants(targets, organism))

        actual_cycle = ecosystem.cycle
        if actual_cycle == ActivityCycle.diurnal:
            ecosystem.cycle = ActivityCycle.nocturnal

        elif actual_cycle == ActivityCycle.nocturnal:
            ecosystem.cycle = ActivityCycle.crepuscular

        elif actual_cycle == ActivityCycle.crepuscular:
            ecosystem.cycle = ActivityCycle.diurnal
            ecosystem.days += 1
        await self.session.commit()
        await self.session.refresh(ecosystem)

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"interaction": results}),
        )
        # Will return the % of the attacker hits the deffender

    async def remove_organism_from_a_ecosystem(
        self, ecosystem_id: UUID, organism_name_or_id: str
    ):
        ecosystem = await self.get(ecosystem_id)
        try:
            organism_id = UUID(organism_name_or_id)
        except (ValueError, TypeError):
            organism_id = None
        organisms = [
            organism
            for organism in ecosystem.organisms
            if (
                organism.id == organism_id or organism.name == organism_name_or_id
                if organism_id
                else organism.name == organism_name_or_id
            )
        ]
        if not organisms:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No organism found in that ecosystem with the ID or name provided.",
            )
        for organism in organisms:
            ecosystem.organisms.remove(organism)
        await self.session.commit()
        return Response(status_code=204)

    async def delete(self, ecosystem_id: UUID):
        ecosystem = await self.get(ecosystem_id)
        if ecosystem:
            await self.session.delete(ecosystem)
            await self.session.commit()
            return Response(status_code=204)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No ecosystem found with the provided ID",
        )
