import uuid
from urllib.parse import parse_qs

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

import managers
import settings
from models import Sites
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


async def check_captcha(client, bad_score=0.5):
    if client.site.captcha_required:
        if client.captcha_token:
            url = 'https://www.google.com/recaptcha/api/siteverify'
            async with httpx.AsyncClient() as c:
                response = await c.post(url, data=dict(secret=client.user.captcha_secret_key,
                                                       response=client.captcha_token, remoteip=client.ip))
                if response.json().get('score', 0) <= bad_score:
                    client.captcha_result = False
                else:
                    client.captcha_result = True
        else:
            client.captcha_result = False
    else:
        client.captcha_result = None


async def get_data_client(request: Request, as_json=True):
    if as_json:
        data = await request.json()
    else:
        data = parse_body(await request.body())
    client = Client(
        ip=request.client.host,
        origin=request.headers.get('origin', ''),
        # redirect=data.pop('_redirect', ''),
        captcha_result=False,
        guid=uuid.UUID(hex=data.pop('_guid')),
    )
    # data.pop('_recaptcha', None),
    if client.guid:
        client.site = await Sites.filter(guid=client.guid).select_related('user').first()
        if client.site:
            client.captcha_token = data.pop('_token', None)
            try:
                await check_captcha(client)
            except Exception as exc:
                print(exc)
                await managers.Inform.send_tg(exc, settings.INFORM_TG_ID)
    return data, client


def fix_slash(url: str, begin=None, end=None):
    if end:
        if not url.endswith('/'):
            url = f"{url}/"
    elif end is False:
        if url.endswith('/'):
            url = url[:-1]
    if begin:
        if not url.startswith('/'):
            url = f"/{url}"
    elif begin is False:
        if url.startswith('/'):
            url = url[1:]
    return url


def make_redirect_url(client: Client):
    redirect_url = client.site.redirect
    if not redirect_url.startswith('http'):
        redirect_url = fix_slash(client.site.domain, end=False) + fix_slash(redirect_url, begin=True)
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
