import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_eco_system(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    response = await client.post("/ecosystem/", json=ecosystem_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Ecosystem test"
    assert response.json()["water_available"] == 1000
    assert response.json()["minimum_water_to_add_per_simulation"] == 50
    assert response.json()["max_water_to_add_per_simulation"] == 200


@pytest.mark.asyncio
async def test_simulate_ecosystem(db_session: AsyncSession, client: AsyncClient):
    ecosystem_payload = {
        "name": "Ecosystem test",
        "water_available": 1000,
        "minimum_water_to_add_per_simulation": 50,
        "max_water_to_add_per_simulation": 200,
    }

    new_ecosystem = await client.post("/ecosystem/", json=ecosystem_payload)
    new_ecosystem_id = new_ecosystem.json()["id"]
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
            "/organism/",
            json=organism["payload"],
            params=organism["params"],
        )

        await client.post(
            "/ecosystem/add_organism_to_a_ecosystem",
            json={
                "eco_system_id": new_ecosystem_id,
                "organism_name": organism["payload"]["name"],
            },
        )

    response = await client.get(f"/ecosystem/{new_ecosystem_id}/simulate")
    assert response.status_code == 200
