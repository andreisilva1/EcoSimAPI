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

    response_for_id = await client.delete(
        f"/organism/{organism_for_id.json()['organism_created']['id']}/delete"
    )

    assert response_for_id.status_code == 204


@pytest.mark.asyncio
async def test_update_organism(db_session: AsyncSession, client: AsyncClient):
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
    }

    organism_created = await client.post(
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

    assert organism_created.status_code == 201

    update_payload = {
        "name": "Super Ant",
        "weight": 1,
        "size": 1,
    }
    response = await client.patch(
        f"/organism/{organism_created.json()['organism_created']['id']}/update",
        json=update_payload,
    )

    assert response.json()["updated_organism"]["name"] == update_payload["name"]
    assert response.json()["updated_organism"]["weight"] == update_payload["weight"]
    assert response.json()["updated_organism"]["size"] == update_payload["size"]


@pytest.mark.asyncio
async def test_get_organism_by_name(db_session: AsyncSession, client: AsyncClient):
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
    }

    organism2_payload = {
        "name": "Super Ant",
        "weight": 0.000003,
        "size": 0.01,
        "age": 0,
        "max_age": 1,
        "reproduction_age": 0,
        "fertility_rate": 50,
        "water_consumption": 0.0001,
        "food_consumption": 0.0002,
    }

    await client.post(
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
    await client.post(
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

    response = await client.get("/organism/?search=Ant")
    assert len(response.json()) == 2
