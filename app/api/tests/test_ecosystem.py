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
    print(response)
    assert response.status_code == 200
