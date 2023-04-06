import os
from urllib.parse import parse_qs

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

import settings
import managers
from serializers import Client

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


async def get_data_client(request: Request):
    body = await request.body()
    data = {key: value[0] for key, value in parse_qs(body.decode()).items()}
    client = Client(
        ip=request.client.host,
        origin=request.headers.get('origin', ''),
        telegram=data.pop('_telegram', None),
        email=data.pop('_email', None),
        redirect=data.pop('_redirect', ''),
    )
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
