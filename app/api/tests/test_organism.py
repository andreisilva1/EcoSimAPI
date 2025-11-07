from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_organism(db_session: AsyncSession, client: AsyncClient):
    organism_payload = {
        "name": "Formiga",
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
        "/organism/",
        json=organism_payload,
        params={
            "type": "omnivore",
            "diet_type": "omnivore",
            "activity_cycle": "diurnal",
            "speed": "fast",
            "social_behavior": "herd",
        },
    )
    assert response.status_code == 200
    assert UUID(response.json()["id"])
