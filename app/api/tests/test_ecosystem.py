import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


# ECOSYSTEM
@pytest.mark.asyncio
async def test_create_eco_system(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    response = await client.post("/ecosystem/create", json=ecosystem_payload)
    assert response.status_code == 201
    assert response.json()["ecosystem_created"]["name"] == "Ecosystem test"
    assert response.json()["ecosystem_created"]["water_available"] == 1000
    assert (
        response.json()["ecosystem_created"]["minimum_water_to_add_per_simulation"]
        == 50
    )
    assert (
        response.json()["ecosystem_created"]["max_water_to_add_per_simulation"] == 200
    )


@pytest.mark.asyncio
async def test_simulate_ecosystem(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    organisms = [
        {
            "payload": {
                "name": "Meerkat",
                "weight": 0.7,
                "size": 0.5,
                "age": 2,
                "max_age": 14,
                "reproduction_age": 2,
                "fertility_rate": 3,
                "water_consumption": 0.1,
                "food_consumption": 0.2,
                "food_sources": "insects",
                "territory_size": 1.0,
            },
            "params": {
                "type": "omnivore",
                "diet_type": "omnivore",
                "activity_cycle": "diurnal",
                "speed": "fast",
                "social_behavior": "herd",
            },
        },
        {
            "payload": {
                "name": "Caracal",
                "weight": 15,
                "size": 1.1,
                "age": 4,
                "max_age": 16,
                "reproduction_age": 3,
                "fertility_rate": 2,
                "water_consumption": 0.5,
                "food_consumption": 3,
                "food_sources": "rodents, birds",
                "territory_size": 5,
            },
            "params": {
                "type": "predator",
                "diet_type": "carnivore",
                "activity_cycle": "nocturnal",
                "speed": "fast",
                "social_behavior": "solitary",
            },
        },
        {
            "payload": {
                "name": "Moose",
                "weight": 500,
                "size": 3.2,
                "age": 6,
                "max_age": 25,
                "reproduction_age": 4,
                "fertility_rate": 1,
                "water_consumption": 5,
                "food_consumption": 18,
                "food_sources": "shrubs, leaves",
                "territory_size": 8,
            },
            "params": {
                "type": "herbivore",
                "diet_type": "herbivore",
                "activity_cycle": "diurnal",
                "speed": "normal",
                "social_behavior": "solitary",
            },
        },
    ]

    for organism in organisms:
        await client.post(
            "/organism/create",
            json=organism["payload"],
            params=organism["params"],
        )

        await client.post(
            "/ecosystem/organism/add",
            json={
                "eco_system_id": new_ecosystem_id,
                "organism_name": organism["payload"]["name"],
            },
        )

    response = await client.get(f"/ecosystem/{new_ecosystem_id}/simulate")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_ecosystem(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }
    ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    response = await client.delete(
        f"/ecosystem/{ecosystem.json()['ecosystem_created']['id']}"
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_ecosystem(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    ecosystem_update_payload = {
        "name": "Testing the Update",
        "water_available": 500,
        "minimum_water_to_add_per_simulation": 100,
        "max_water_to_add_per_simulation": 250,
    }

    response = await client.patch(
        f"/ecosystem/{new_ecosystem_id}", json=ecosystem_update_payload
    )

    assert (
        response.json()["updated_ecosystem"]["name"] == ecosystem_update_payload["name"]
    )
    assert (
        response.json()["updated_ecosystem"]["water_available"]
        == ecosystem_update_payload["water_available"]
    )
    assert (
        response.json()["updated_ecosystem"]["minimum_water_to_add_per_simulation"]
        == ecosystem_update_payload["minimum_water_to_add_per_simulation"]
    )
    assert (
        response.json()["updated_ecosystem"]["max_water_to_add_per_simulation"]
        == ecosystem_update_payload["max_water_to_add_per_simulation"]
    )


# ORGANISM
@pytest.mark.asyncio
async def test_get_all_organisms_from_a_ecosystem(
    db_session: AsyncSession, client: AsyncClient
):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    organism = {
        "payload": {
            "name": "Meerkat",
            "weight": 0.7,
            "size": 0.5,
            "age": 2,
            "max_age": 14,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_consumption": 0.1,
            "food_consumption": 0.2,
            "territory_size": 1.0,
        },
        "params": {
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    }

    new_organism = await client.post(
        "/organism/create",
        json=organism["payload"],
        params=organism["params"],
    )
    await client.post(
        f"/ecosystem/organism/add?organism_name={new_organism.json()['organism_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    response = await client.get(
        f"/ecosystem/{new_ecosystem_id}/organisms",
    )

    assert response.status_code == 200
    assert len(response.json()["all_organisms"]) == 1


@pytest.mark.asyncio
async def test_add_organism_from_a_ecosystem(
    db_session: AsyncSession, client: AsyncClient
):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    organism = {
        "payload": {
            "name": "Meerkat",
            "weight": 0.7,
            "size": 0.5,
            "age": 2,
            "max_age": 14,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_consumption": 0.1,
            "food_consumption": 0.2,
            "territory_size": 1.0,
        },
        "params": {
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    }

    new_organism = await client.post(
        "/organism/create",
        json=organism["payload"],
        params=organism["params"],
    )

    response = await client.post(
        f"/ecosystem/organism/add?organism_name={new_organism.json()['organism_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_update_organism_ecosystem(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    organism = {
        "payload": {
            "name": "Meerkat",
            "weight": 0.7,
            "size": 0.5,
            "age": 2,
            "max_age": 14,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_consumption": 0.1,
            "food_consumption": 0.2,
            "territory_size": 1.0,
        },
        "params": {
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    }

    plant = {
        "payload": {
            "name": "Arbust",
            "weight": 50,
            "size": 3,
            "age": 0,
            "max_age": 15,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_need": 5,
        },
        "params": {"type": "tree"},
    }
    new_organism = await client.post(
        "/organism/create",
        json=organism["payload"],
        params=organism["params"],
    )

    new_plant = await client.post(
        "/plant/create", json=plant["payload"], params=plant["params"]
    )

    new_pollination_target = {
        "pollination_target": new_plant.json()["plant_created"]["name"]
    }

    await client.post(
        f"/ecosystem/organism/add?organism_name={new_organism.json()['organism_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    response = await client.patch(
        f"/ecosystem/organisms/{new_organism.json()['organism_created']['name']}/update?ecosystem_id={new_ecosystem_id}",
        json=new_pollination_target,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_organism_from_a_ecosystem(
    db_session: AsyncSession, client: AsyncClient
):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    organism = {
        "payload": {
            "name": "Meerkat",
            "weight": 0.7,
            "size": 0.5,
            "age": 2,
            "max_age": 14,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_consumption": 0.1,
            "food_consumption": 0.2,
            "territory_size": 1.0,
        },
        "params": {
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    }

    new_organism = await client.post(
        "/organism/create",
        json=organism["payload"],
        params=organism["params"],
    )

    added_to_ecosystem = await client.post(
        f"/ecosystem/organism/add?organism_name={new_organism.json()['organism_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    response_id = await client.delete(
        f"/ecosystem/{new_ecosystem_id}/organism/{added_to_ecosystem.json()['added_to_ecosystem']['id']}/remove"
    )

    assert response_id.status_code == 204


# PLANTS
@pytest.mark.asyncio
async def test_get_all_plants_from_a_ecosystem(
    db_session: AsyncSession, client: AsyncClient
):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    plant = {
        "payload": {
            "name": "Arbust",
            "weight": 50,
            "size": 3,
            "age": 0,
            "max_age": 15,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_need": 5,
        },
        "params": {"type": "tree"},
    }

    new_plant = await client.post(
        "/plant/create",
        json=plant["payload"],
        params=plant["params"],
    )
    await client.post(
        f"/ecosystem/plant/add?plant_name={new_plant.json()['plant_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    response = await client.get(
        f"/ecosystem/{new_ecosystem_id}/plants",
    )

    assert response.status_code == 200
    assert len(response.json()["all_plants"]) == 1


@pytest.mark.asyncio
async def test_add_plant_from_a_ecosystem(
    db_session: AsyncSession, client: AsyncClient
):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    plant = {
        "payload": {
            "name": "Arbust",
            "weight": 50,
            "size": 3,
            "age": 0,
            "max_age": 15,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_need": 5,
        },
        "params": {"type": "tree"},
    }

    new_plant = await client.post(
        "/plant/create",
        json=plant["payload"],
        params=plant["params"],
    )

    response = await client.post(
        f"/ecosystem/plant/add?plant_name={new_plant.json()['plant_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_update_plant_ecosystem(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    organism = {
        "payload": {
            "name": "Meerkat",
            "weight": 0.7,
            "size": 0.5,
            "age": 2,
            "max_age": 14,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_consumption": 0.1,
            "food_consumption": 0.2,
            "territory_size": 1.0,
        },
        "params": {
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    }

    plant = {
        "payload": {
            "name": "Arbust",
            "weight": 50,
            "size": 3,
            "age": 0,
            "max_age": 15,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_need": 5,
        },
        "params": {"type": "tree"},
    }
    new_organism = await client.post(
        "/organism/create",
        json=organism["payload"],
        params=organism["params"],
    )

    new_plant = await client.post(
        "/plant/create", json=plant["payload"], params=plant["params"]
    )

    # ADD ORGANISM TO THE ECOSYSTEM
    await client.post(
        f"/ecosystem/organism/add?organism_name={new_organism.json()['organism_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    # ADD PLANT TO THE ECOSYSTEM
    await client.post(
        f"/ecosystem/plant/add?plant_name={new_plant.json()['plant_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    new_pollinator = {"pollinators": new_organism.json()["organism_created"]["name"]}

    response = await client.patch(
        f"/ecosystem/plants/{new_plant.json()['plant_created']['name']}/update?ecosystem_id={new_ecosystem_id}",
        json=new_pollinator,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_plant_from_a_ecosystem(
    db_session: AsyncSession, client: AsyncClient
):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/create", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["ecosystem_created"]["id"]
    plant = {
        "payload": {
            "name": "Arbust",
            "weight": 50,
            "size": 3,
            "age": 0,
            "max_age": 15,
            "reproduction_age": 2,
            "fertility_rate": 3,
            "water_need": 5,
        },
        "params": {"type": "tree"},
    }

    new_plant = await client.post(
        "/plant/create",
        json=plant["payload"],
        params=plant["params"],
    )

    added_to_ecosystem = await client.post(
        f"/ecosystem/plant/add?plant_name={new_plant.json()['plant_created']['name']}&ecosystem_id={new_ecosystem_id}",
    )

    response_id = await client.delete(
        f"/ecosystem/{new_ecosystem_id}/plant/{added_to_ecosystem.json()['added_to_ecosystem']['id']}/remove"
    )

    assert response_id.status_code == 204
