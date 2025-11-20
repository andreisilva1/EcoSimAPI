import random
from typing import List
from uuid import UUID, uuid4

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.exceptions.exceptions import (
    BLANK_UPDATE_FIELDS,
    RESOURCE_ID_NOT_FOUND,
    RESOURCE_NAME_ALREADY_EXISTS,
    RESOURCE_NAME_NOT_FOUND,
    RESOURCE_NOT_FOUND_IN_RELATIONSHIP,
)
from app.api.interactions.interaction_functions import (
    collect_and_transport_nectar,
    drink_water,
    graze_plants,
    hunt_prey,
    reproduce,
    rest,
)
from app.api.schemas.ecosystem import (
    CreateEcoSystem,
    UpdateEcoSystem,
)
from app.api.schemas.organism import UpdateEcosystemOrganism
from app.api.schemas.plant import UpdateEcosystemPlant
from app.database.enums import ActivityCycle, OrganismType
from app.database.interactions_list import ACTIONS_BY_ORGANISM_TYPE
from app.database.models import Ecosystem, Organism, Plant


class EcoSystemService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, ecosystem_id: UUID):
        ecosystem = await self.session.scalar(
            select(Ecosystem)
            .where(Ecosystem.id == ecosystem_id)
            .options(
                selectinload(Ecosystem.organisms).selectinload(Organism.prey),
                selectinload(Ecosystem.organisms).selectinload(Organism.predator),
                selectinload(Ecosystem.organisms).selectinload(
                    Organism.pollination_target
                ),
                selectinload(Ecosystem.plants).selectinload(Plant.pollinators),
            )
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
        if not ecosystem:
            raise RESOURCE_ID_NOT_FOUND("ecosystem")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"all_organisms": ecosystem.organisms}),
        )

    async def get_all_ecosystem_plants(self, ecosystem_name_or_id: str):
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
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"all_plants": ecosystem.plants}),
        )

    async def get_pollination_targets_in_the_ecosystem(
        self, organism: Organism, ecosystem: Ecosystem
    ):
        pollination_targets_in_the_ecosystem = []
        for target in organism.pollination_target:
            for plant in ecosystem.plants:
                if plant.name == target.name:
                    pollination_targets_in_the_ecosystem.append(plant)
        return pollination_targets_in_the_ecosystem

    async def add(self, ecosystem: CreateEcoSystem):
        query = await self.session.execute(
            select(Ecosystem).where((func.lower(Ecosystem.name) == ecosystem.name))
        )
        existent_ecosystem = query.scalar_one_or_none()
        if existent_ecosystem:
            raise RESOURCE_NAME_ALREADY_EXISTS("ecosystem")
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
            raise BLANK_UPDATE_FIELDS()
        for key, value in updates.items():
            setattr(ecosystem, key, value)
        await self.session.commit()
        await self.session.refresh(ecosystem)
        return JSONResponse(
            status_code=200, content=jsonable_encoder({"updated_ecosystem": ecosystem})
        )

    async def extract_organism_by_name(self, name: str):
        organism = await self.session.execute(
            select(Organism)
            .where((Organism.name == name) & (Organism.ecosystem_id.is_(None)))
            .options(selectinload(Organism.prey), selectinload(Organism.predator))
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

    async def extract_plants_from_a_specific_ecosystem_by_name(
        self, ecosystem_id: UUID, name: str
    ):
        ecosystem = await self.session.execute(
            select(Ecosystem).where(Ecosystem.id == ecosystem_id)
        )
        ecosystem = ecosystem.scalar_one_or_none()
        if ecosystem:
            plants = [
                organism for organism in ecosystem.plants if organism.name == name
            ]
        return plants

    async def extract_plant_by_name(self, name: str):
        plant = await self.session.scalars(select(Plant).where(Plant.name == name))
        return plant.first()

    async def convert_pollination_target_to_plant(
        self, pollination_target
    ) -> List[Plant]:
        targets = []
        for target in pollination_target:
            plant = await self.session.execute(
                select(Plant).where(Plant.name == target)
            )
            plant = plant.scalar_one_or_none()
            if plant:
                targets.append(plant)
        return targets

    async def add_plant_to_a_ecosystem(
        self, ecosystem_id: UUID, plant_name: str, return_json: bool = True
    ):
        ecosystem = await self.get(ecosystem_id)

        plant = await self.extract_plant_by_name(plant_name)

        if not plant:
            raise RESOURCE_NAME_NOT_FOUND("plant")

        new_plant_to_this_ecosystem = Plant(
            **plant.model_dump(exclude=["id", "health", "age"]), id=uuid4()
        )
        ecosystem.plants.append(new_plant_to_this_ecosystem)
        await self.session.commit()
        if return_json:
            return JSONResponse(
                status_code=201,
                content=jsonable_encoder(
                    {"added_to_ecosystem": new_plant_to_this_ecosystem}
                ),
            )

    async def add_organism_to_a_eco_system(
        self, ecosystem_id: UUID, organism_name: str, return_json: bool = True
    ):
        ecosystem = await self.get(ecosystem_id)

        organism = await self.extract_organism_by_name(organism_name)

        if not organism:
            raise RESOURCE_NAME_NOT_FOUND("organism")

        new_organism_to_this_ecosystem = Organism(
            **organism.model_dump(exclude=["id"]),
            id=uuid4(),
            pollination_target=organism.pollination_target,
            prey=organism.prey,
            predator=organism.predator,
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
        organisms = await self.extract_organisms_from_a_specific_ecosystem_by_name(
            ecosystem.id, organism_name
        )
        if not ecosystem:
            raise RESOURCE_ID_NOT_FOUND("ecosystem")
        if not organisms:
            raise RESOURCE_NOT_FOUND_IN_RELATIONSHIP(one="ecosystem", many="orgnaism")

        updated_fields = {}
        for key, value in updated_organism.model_dump().items():
            if value:
                updated_fields[key] = value

        for field in updated_fields:
            entities_to_add = (
                updated_fields[field].split(",")
                if "," in updated_fields[field]
                else [updated_fields[field]]
            )
            for entity in entities_to_add:
                if field == "pollination_target":
                    entities_in_the_ecosystem = (
                        await self.extract_plants_from_a_specific_ecosystem_by_name(
                            ecosystem_id, entity
                        )
                    )

                else:
                    entities_in_the_ecosystem = (
                        await self.extract_organisms_from_a_specific_ecosystem_by_name(
                            ecosystem_id, entity
                        )
                    )
                if entities_in_the_ecosystem:
                    for organism in organisms:
                        list_entities = getattr(organism, field)
                        for entity_in_the_ecosystem in entities_in_the_ecosystem:
                            list_entities.append(entity_in_the_ecosystem)
                    await self.session.commit()
        return JSONResponse(
            status_code=200, content={"message": f"Organism {organism_name} updated."}
        )

    async def update_ecosystem_plant(
        self, ecosystem_id, plant_name, updated_plant: UpdateEcosystemPlant
    ):
        ecosystem = await self.get(ecosystem_id)
        plants = await self.extract_plants_from_a_specific_ecosystem_by_name(
            ecosystem.id, plant_name
        )
        if not ecosystem:
            raise RESOURCE_ID_NOT_FOUND("ecosystem")

        if not plants:
            raise RESOURCE_NOT_FOUND_IN_RELATIONSHIP(one="ecosystem", many="plant")

        updated_fields = {}
        for key, value in updated_plant.model_dump().items():
            if value:
                updated_fields[key] = value

        for field in updated_fields:
            entities_to_add = (
                updated_fields[field].split(",")
                if "," in updated_fields[field]
                else updated_fields[field]
            )

            for entity in entities_to_add:
                if field == "pollinators":
                    entities_in_the_ecosystem = await self.extract_organism_by_name(
                        entity
                    )

                else:
                    entities_in_the_ecosystem = (
                        await self.extract_plants_from_a_specific_ecosystem_by_name(
                            ecosystem_id, entity
                        )
                    )
                if entities_in_the_ecosystem:
                    for plant in plants:
                        list_entities = getattr(plant, field)
                        for entity_in_the_ecosystem in entities_in_the_ecosystem:
                            list_entities.append(entity_in_the_ecosystem)
                    await self.session.commit()
        return JSONResponse(
            status_code=200, content={"message": f"Plant {plant_name} updated."}
        )

    async def simulate(self, ecosystem_id: UUID):
        ecosystem = await self.get(ecosystem_id)
        results = []
        results.append({"time": ecosystem.cycle})
        organisms: List[Organism] = ecosystem.organisms
        plants: List[Plant] = ecosystem.plants

        for organism in organisms:
            food_consumed = 0
            possible_interactions = ACTIONS_BY_ORGANISM_TYPE[organism.type]
            actions = random.sample(possible_interactions, 2)
            for action in actions:
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
                                        organism.pollination_target
                                    )
                                )
                                if not targets:
                                    results.append(
                                        {f"No pollinators found for {organism.name}"}
                                    )
                                else:
                                    results.append(graze_plants(targets, organism))
                elif organism.type == OrganismType.pollinator:
                    if action == "collect_nectar":
                        pollination_targets_in_ecosystem = (
                            await self.get_pollination_targets_in_the_ecosystem(
                                organism, ecosystem
                            )
                        )
                        if (
                            not organism.pollination_target
                            or not pollination_targets_in_ecosystem
                        ):
                            results.append(
                                {
                                    f"No {organism.name} pollination targets found in this ecosystem "
                                }
                            )
                        else:
                            (
                                results_collect_nectar,
                                results_transport_nectar,
                                plant_to_transport_nectar,
                                plant_to_transport_nectar_population_increment,
                            ) = collect_and_transport_nectar(
                                organism, pollination_targets_in_ecosystem
                            )
                            for _ in range(
                                plant_to_transport_nectar_population_increment
                            ):
                                await self.add_plant_to_a_ecosystem(
                                    ecosystem.id, plant_to_transport_nectar.name
                                )
                            results.append(
                                [results_collect_nectar, results_transport_nectar],
                            )

            if (
                organism.health <= 0
                or organism.thirst >= 100
                or organism.hunger >= 100
                or organism.age > organism.max_age
            ):
                results.append(await self.death_cause_and_delete_organism(organism))
                continue

            if food_consumed < organism.food_consumption:
                HEALTH_LOST = random.randint(5, 15)
                organism.health -= HEALTH_LOST
                results.append(
                    {
                        f"{organism.name} don't eat the sufficient for the day and lost {HEALTH_LOST}"
                    }
                )

        for plant in plants:
            if plant.weight <= 0 or plant.age >= plant.max_age:
                results.append(await self.death_cause_and_delete_organism(plant))
            else:
                results.append(drink_water(ecosystem, plant))

        actual_cycle = ecosystem.cycle
        if actual_cycle == ActivityCycle.diurnal:
            ecosystem.cycle = ActivityCycle.nocturnal

        elif actual_cycle == ActivityCycle.nocturnal:
            ecosystem.cycle = ActivityCycle.crepuscular

        elif actual_cycle == ActivityCycle.crepuscular:
            ecosystem.cycle = ActivityCycle.diurnal
            ecosystem.days += 1
            WATER_TO_ADD = random.randint(
                ecosystem.minimum_water_to_add_per_simulation,
                ecosystem.max_water_to_add_per_simulation,
            )
            ecosystem.water_available += WATER_TO_ADD
            results.append({f"{WATER_TO_ADD} water were added to the ecosystem."})
            if ecosystem.days % 3 == 0:
                ecosystem.year += 1

                for entity in (*ecosystem.organisms, *ecosystem.plants):
                    entity.age += 1

        await self.session.commit()

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"interaction": results}),
        )

    async def remove_organism_from_a_ecosystem(
        self, ecosystem_id: UUID, organism_name_or_id: UUID | str
    ):
        ecosystem = await self.get(ecosystem_id)
        organisms_to_delete = []
        try:
            organism_uuid = UUID(str(organism_name_or_id))
        except (ValueError, TypeError):
            organism_uuid = None

        organisms_to_delete = [
            organism
            for organism in ecosystem.organisms
            if (organism_uuid is not None and organism.id == organism_uuid)
            or (organism.name == organism_name_or_id)
        ]

        if not organisms_to_delete:
            raise RESOURCE_NOT_FOUND_IN_RELATIONSHIP(one="ecosystem", many="organism")

        for organism in organisms_to_delete:
            ecosystem.organisms.remove(organism)
            await self.session.delete(organism)
        await self.session.commit()
        await self.session.refresh(ecosystem)
        return Response(status_code=204)

    async def remove_plant_from_a_ecosystem(
        self, ecosystem_id: UUID, plant_name_or_id: str
    ):
        ecosystem = await self.get(ecosystem_id)
        plants_to_delete = []
        try:
            plant_uuid = UUID(str(plant_name_or_id))
        except (ValueError, TypeError):
            plant_uuid = None

        plants_to_delete = [
            plant
            for plant in ecosystem.plants
            if (plant_uuid is not None and plant.id == plant_uuid)
            or (plant.name == plant_name_or_id)
        ]

        if not plants_to_delete:
            raise RESOURCE_NOT_FOUND_IN_RELATIONSHIP(one="ecosystem", many="plant")
        for plant in plants_to_delete:
            ecosystem.plants.remove(plant)
            await self.session.delete(plant)
        await self.session.commit()
        await self.session.refresh(ecosystem)
        return Response(status_code=204)

    async def delete(self, ecosystem_id: UUID):
        ecosystem = await self.get(ecosystem_id)
        if ecosystem:
            await self.session.delete(ecosystem)
            await self.session.commit()
            return Response(status_code=204)
        raise RESOURCE_ID_NOT_FOUND("ecosystem")

    async def death_cause_and_delete_organism(self, organism: Organism | Plant):
        await self.session.delete(organism)
        await self.session.commit()
        if organism.health <= 0:
            return f"{organism.name}'s health reached 0. {organism.name} is dead."
        if organism.age > organism.max_age:
            return f"{organism.name} has reached its max age. {organism.name} is dead."

        if type(organism) is Organism:
            if organism.thirst >= 100:
                return f"{organism.name}'s thirst reached 100. {organism.name} is dead."

            if organism.hunger >= 100:
                return f"{organism.name}'s hunger reached 100. {organism.name} is dead."
        elif type(organism) is Plant:
            if organism.weight <= 0:
                return {f"{organism.name}'s weight reached 0. {organism.name} is dead."}
