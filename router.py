from fastapi import APIRouter, BackgroundTasks, Request
from starlette import status
from starlette.responses import RedirectResponse, Response

from helpers import get_data_client, make_redirect_url, run_inform
from serializers import BaseResult

secret_router = APIRouter()
clean_router = APIRouter()


@secret_router.post("/inform", response_model=BaseResult)
async def inform_post(request: Request, background_tasks: BackgroundTasks):
    """Отправка уведомления (для форм обратной связи с js)"""
    data, client = await get_data_client(request)
    if not client.site:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    if client.captcha_result is False:
        return Response(status_code=status.HTTP_406_NOT_ACCEPTABLE)
    await run_inform(data, client, background_tasks)
    return BaseResult(result='OK')


@clean_router.post("/info")
async def info_post(request: Request, background_tasks: BackgroundTasks):
    """
    Отправка уведомления (для форм обратной связи без js)
    <form method="POST" action="https://direct.electis.ru/info">
    <input type="hidden" name="_guid" value="1234567" />
    """
    data, client = await get_data_client(request, as_json=False)
    await run_inform(data, client, background_tasks)
    redirect_url = make_redirect_url(client)
    print(f"Redirect to {redirect_url}")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
