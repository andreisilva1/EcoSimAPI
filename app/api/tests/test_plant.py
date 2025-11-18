from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_plant(db_session: AsyncSession, client: AsyncClient):
    plant_payload = {
        "name": "Testing Plant",
        "weight": 0,
        "age": 0,
        "reproduction_age": 0,
        "population": 1,
        "size": 0,
        "max_age": 0,
        "fertility_rate": 0,
        "water_need": 5,
    }

    response = await client.post(
        "/plant/create",
        json=plant_payload,
        params={"type": "tree"},
    )
    assert response.status_code == 201
    assert UUID(response.json()["plant_created"]["id"])


@pytest.mark.asyncio
async def test_search_plant(db_session: AsyncSession, client: AsyncClient):
    plant_payload = {
        "name": "Testing Plant",
        "weight": 0,
        "age": 0,
        "reproduction_age": 0,
        "size": 0,
        "max_age": 0,
        "fertility_rate": 0,
        "water_need": 5,
    }

    await client.post(
        "/plant/create",
        json=plant_payload,
        params={"type": "tree"},
    )

    response = await client.get(f"/plant/?search={plant_payload['name']}")
    assert response.status_code == 200
    assert len(response.json()["plants"]) == 1


@pytest.mark.asyncio
async def test_update_plant(db_session: AsyncSession, client: AsyncClient):
    plant_payload = {
        "name": "Testing Plant",
        "weight": 0,
        "age": 0,
        "reproduction_age": 0,
        "size": 0,
        "max_age": 0,
        "fertility_rate": 0,
        "water_need": 5,
    }

    update_infos = {"name": "Updated Plant"}

    plant_created = await client.post(
        "/plant/create",
        json=plant_payload,
        params={"type": "tree"},
    )

    response = await client.patch(
        f"/plant/{plant_created.json()['plant_created']['id']}/update",
        json=update_infos,
    )

    assert response.status_code == 200
    assert response.json()["updated_plant"]["name"] == update_infos["name"]


@pytest.mark.asyncio
async def test_delete_plant(db_session: AsyncSession, client: AsyncClient):
    plant_payload = {
        "name": "Testing Plant",
        "weight": 0,
        "age": 0,
        "reproduction_age": 0,
        "size": 0,
        "max_age": 0,
        "fertility_rate": 0,
        "water_need": 5,
    }

    plant_created = await client.post(
        "/plant/create",
        json=plant_payload,
        params={"type": "tree"},
    )

    response = await client.delete(
        f"/plant/{plant_created.json()['plant_created']['id']}/delete"
    )

    assert response.status_code == 204
