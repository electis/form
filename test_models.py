import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

import settings
from main import app
from managers import Inform
from models import Users


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as c:
            yield c


@pytest.mark.anyio
async def test_info(client: AsyncClient):
    user_obj = await Users.create(email='test@mail.com', telegram=123)

    data = dict(_guid=user_obj.guid.hex, _redirect='http://test')

    async def send_tg(self, text, tg_id=None):
        assert tg_id == user_obj.telegram

    async def send_email(self, text, email):
        assert email == user_obj.email

    Inform.send_tg = send_tg
    Inform.send_email = send_email

    response = await client.post("/info", data=data)
    assert response.status_code == 303
    assert response.headers.get('location') == data['_redirect']


@pytest.mark.anyio
async def test_inform(client: AsyncClient):
    user_obj = await Users.create(email='test@mail.com', telegram=123)

    data = dict(_guid=user_obj.guid.hex, _redirect='http://test')
    headers = dict(Authorization=f"Bearer {settings.SECRET_TOKEN}")

    async def send_tg(self, text, tg_id=None):
        assert tg_id == user_obj.telegram

    async def send_email(self, text, email):
        assert email == user_obj.email

    Inform.send_tg = send_tg
    Inform.send_email = send_email

    response = await client.post("/inform", headers=headers, json=data)
    assert response.status_code == 200