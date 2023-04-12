"""pytest required"""
import os

os.environ['ENVIRONMENT'] = 'test'
os.environ['INFORM_TG_TOKEN'] = 'qwe'

from fastapi.testclient import TestClient
from main import app
from managers import Inform
import settings

client = TestClient(app)

# TODO переделать


def test_inform_auth():
    response = client.post("/inform", headers=dict())
    assert response.status_code == 401

    response = client.post("/inform", headers=dict(Authorization=f"Bearer {settings.SECRET_TOKEN}"))
    assert response.status_code == 200


def test_inform():
    data = dict(_telegram='123', _email='test@email.com')

    async def send_tg(self, text, tg_id=None):
        assert tg_id, data['_telegram']

    async def send_email(self, text, email):
        assert email, data['_email']

    Inform.send_tg = send_tg
    Inform.send_email = send_email

    response = client.post("/inform", headers=dict(Authorization=f"Bearer {settings.SECRET_TOKEN}"), data=data)
    assert response.status_code == 200


def test_info():
    data = dict(_telegram='123', _email='test@email.com', _redirect='http://test')

    async def send_tg(self, text, tg_id=None):
        assert tg_id, data['_telegram']

    async def send_email(self, text, email):
        assert email, data['_email']

    Inform.send_tg = send_tg
    Inform.send_email = send_email

    response = client.post("/info", data=data)
    assert response.history[0].status_code == 303
    assert response.history[0].headers.get('location') == data['_redirect']
