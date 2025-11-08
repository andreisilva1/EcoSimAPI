from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_organism(db_session: AsyncSession, client: AsyncClient):
    organism_payload = {
        "name": "Ant",
        "weight": 0.000003,
        "size": 0.01,
        "age": 0,
        "max_age": 1,
        "reproduction_age": 0,
        "fertility_rate": 50,
        "water_consumption": 0.0001,
        "food_consumption": 0.0002,
        "food_sources": "plant matter, insects",
        "territory_size": 0,
    }

    response = await client.post(
        "/organism/create",
        json=organism_payload,
        params={
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    )
    assert response.status_code == 201
    assert UUID(response.json()["organism_created"]["id"])


@pytest.mark.asyncio
async def test_delete_organism(db_session, client: AsyncClient):
    organism1_payload = {
        "name": "Ant",
        "weight": 0.000003,
        "size": 0.01,
        "age": 0,
        "max_age": 1,
        "reproduction_age": 0,
        "fertility_rate": 50,
        "water_consumption": 0.0001,
        "food_consumption": 0.0002,
        "food_sources": "plant matter, insects",
        "territory_size": 0,
    }

    organism2_payload = {
        "name": "Ant",
        "weight": 0.000003,
        "size": 0.01,
        "age": 0,
        "max_age": 1,
        "reproduction_age": 0,
        "fertility_rate": 50,
        "water_consumption": 0.0001,
        "food_consumption": 0.0002,
        "food_sources": "plant matter, insects",
        "territory_size": 0,
    }

    organism_for_id = await client.post(
        "/organism/create",
        json=organism1_payload,
        params={
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    )
    organism_for_name = await client.post(
        "/organism/create",
        json=organism2_payload,
        params={
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    )

    response_for_id = await client.delete(
        f"/organism/{organism_for_id.json()['organism_created']['id']}/delete"
    )
    response_for_name = await client.delete(
        f"/organism/{organism_for_name.json()['organism_created']['name']}/delete"
    )

    assert response_for_id.status_code == 204
    assert response_for_name.status_code == 204
