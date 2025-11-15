import random
from typing import List
from uuid import UUID, uuid4

from fastapi import HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.ecosystem import (
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
                (Ecosystem.name == ecosystem_name_or_id or Ecosystem.id == valid_uuid)
                if valid_uuid
                else Ecosystem.name == ecosystem_name_or_id
            )
        )
        ecosystem = ecosystem.scalar_one_or_none()
        return ecosystem.organisms

    async def get_pollination_targets_in_the_ecosystem(
        self, organism: Organism, ecosystem: Ecosystem
    ):
        pollination_targets_in_the_ecosystem = []
        for target in organism.pollination_target:
            if target in ecosystem.plants:
                pollination_targets_in_the_ecosystem.append(target)
        return pollination_targets_in_the_ecosystem

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
        organism = await self.session.scalars(
            select(Organism).where(Organism.name == name)
        )
        return organism.first()

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
        self, ecosystem_id: UUID, organism_name: str, return_json: bool = True
    ):
        ecosystem = await self.get(ecosystem_id)

        organism = await self.extract_organism_by_name(organism_name)

        if not organism:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No organism found with the provided name.",
            )

        new_organism_to_this_ecosystem = Organism(
            **organism.model_dump(exclude=["id"]), id=uuid4()
        )
        ecosystem.organisms.append(new_organism_to_this_ecosystem)
        await self.session.commit()
        if return_json:
            return JSONResponse(
                status_code=201,
                content=jsonable_encoder(
                    {"added_to_ecosystem": new_organism_to_this_ecosystem}
                ),
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
        organisms: List[Organism] = ecosystem.organisms
        for organism in organisms:
            food_consumed = 0
            possible_interactions = ACTIONS_BY_TYPE[organism.type]
            actions = random.sample(possible_interactions, 2)
            for action in actions:
                if (
                    organism.health <= 0
                    or organism.thirst >= 100
                    or organism.hunger >= 100
                ):
                    results.append(await self.death_cause_and_delete_organism(organism))
                    break

                if action == "rest":
                    results.append(rest(organism))

                if action == "reproduce" and organism.age >= organism.reproduction_age:
                    if not organism.pregnant:
                        organism_to_reproduce = await self.session.scalars(
                            select(Organism).where(
                                Organism.name == organism.name,
                                Organism.id != organism.id,
                                Organism.pregnant.is_(False),
                            )
                        )
                        organism_to_reproduce = organism_to_reproduce.all()
                        if organism_to_reproduce:
                            results.append(reproduce(organism_to_reproduce))
                        else:
                            results.append(
                                {f"No partner has been found to {organism.name}."}
                            )
                    else:
                        organism.pregnant = False
                        await self.add_organism_to_a_eco_system(
                            ecosystem.id, organism.name, False
                        )
                        results.append({f"A new {organism.name} has born!"})

                if action == "drink_water":
                    results.append(drink_water(ecosystem, organism))

                if organism.type == OrganismType.predator:
                    if action == "hunt_prey":
                        attacker = organism
                        deffender = random.choice(organisms)
                        while deffender == attacker:
                            deffender = random.choice(organisms)
                        results.append(hunt_prey(attacker, deffender))
                        if deffender.health <= 0:
                            food_consumed += random.randint(
                                0, int(deffender.weight // 2)
                            )

                elif organism.type == OrganismType.herbivore:
                    if action == "graze_plants":
                        pollination_targets_in_the_ecosystem = (
                            await self.get_pollination_targets_in_the_ecosystem(
                                organism, ecosystem
                            )
                        )
                        pollination_target = random.choice(
                            pollination_targets_in_the_ecosystem
                        )
                        results.append(graze_plants(pollination_target, organism))

                elif organism.type == OrganismType.omnivore:
                    if action == "find_food":
                        action = random.choice(["hunt_prey", "graze_plants"])
                        match action:
                            case "hunt_prey":
                                results.append(hunt_prey(organism, organisms))
                            case "graze_plants":
                                targets = (
                                    await self.convert_pollination_target_to_plant(
                                        organism.pollinators
                                    )
                                )
                                if not targets:
                                    results.append(
                                        {f"No pollinators found for {organism.name}"}
                                    )
                                else:
                                    results.append(graze_plants(targets, organism))

            if food_consumed < organism.food_consumption:
                HEALTH_LOST = random.randint(5, 15)
                organism.health -= HEALTH_LOST
                results.append(
                    {
                        f"{organism.name} don't eat the sufficient for the day and lost {HEALTH_LOST}"
                    }
                )

        actual_cycle = ecosystem.cycle
        if actual_cycle == ActivityCycle.diurnal:
            ecosystem.cycle = ActivityCycle.nocturnal

        elif actual_cycle == ActivityCycle.nocturnal:
            ecosystem.cycle = ActivityCycle.crepuscular

        elif actual_cycle == ActivityCycle.crepuscular:
            ecosystem.cycle = ActivityCycle.diurnal
            ecosystem.days += 1
        await self.session.commit()

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
            organism_uuid = UUID(organism_name_or_id)
        except (ValueError, TypeError):
            organism_uuid = None

        organisms = [
            organism
            for organism in ecosystem.organisms
            if (
                (organism.name == organism_name_or_id or organism.id == organism_uuid)
                if organism_uuid
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

    async def death_cause_and_delete_organism(self, organism: Organism):
        await self.session.delete(organism)
        await self.session.commit()
        if organism.health <= 0:
            return f"{organism.name} health reaches 0. {organism.name} is dead."

        if organism.thirst >= 100:
            return f"{organism.name} thirst reaches 100. {organism.name} is dead."

        if organism.hunger >= 100:
            return f"{organism.name} hunger reaches 100. {organism.name} is dead."
