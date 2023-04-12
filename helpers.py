import os
from urllib.parse import parse_qs

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

import settings
import managers
from local.users import users
from serializers import Client, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def auth(token: str = Depends(oauth2_scheme)):
    """Реализует аутентификацию по токену для всех методов"""
    if token == settings.SECRET_TOKEN:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def check_captcha(client):
    if client.user.captcha_required:
        if client.captcha_token:
            url = 'https://www.google.com/recaptcha/api/siteverify'
            async with httpx.AsyncClient() as c:
                response = await c.post(url, data=dict(secret=client.user.captcha_secret_key,
                                                       response=client.captcha_token, remoteip=client.ip))
                if response.json().get('score', 0) <= 0.5:
                    client.captcha_result = False
                else:
                    client.captcha_result = True
        else:
            client.captcha_result = False
    else:
        client.captcha_result = None


async def get_data_client(request: Request):
    data = await request.json()
    client = Client(
        ip=request.client.host,
        origin=request.headers.get('origin', ''),
        redirect=data.pop('_redirect', ''),
    )
    if (guid := data.pop('_guid')) and (user := users.get(guid)):
        client.captcha_token = data.pop('_token', None)
        # TODO user from db
        client.user = user
        await check_captcha(client)
    return data, client


def make_redirect_url(client: Client):
    redirect_url = client.redirect
    if not redirect_url.startswith('http'):
        if redirect_url.startswith('/'):
            redirect_url = redirect_url[1:]
        redirect_url = os.path.join(client.origin, redirect_url)
    return redirect_url


async def inform_post(data: dict, client: Client):
    """Отправка уведомления"""
    obj = managers.Inform(data, client)
    await obj.inform()


async def run_inform(data: dict, client: Client, background_tasks):
    if settings.DEBUG:
        await inform_post(data, client)
    else:
        background_tasks.add_task(inform_post, data, client)

def parse_body(body):
    return {key: value[0] for key, value in parse_qs(body.decode()).items()}