from typing import Optional

from pydantic import BaseModel


class BaseResult(BaseModel):
    """Основной ответ сервиса"""
    result: Optional[str]


class User(BaseModel):
    guid: str
    # tg_bot: Optional[str]
    telegram: Optional[int]
    email: Optional[str]
    captcha_required: Optional[bool]
    captcha_key: Optional[str]
    captcha_secret_key: Optional[str]


class Client(BaseModel):
    ip: Optional[str]
    origin: Optional[str]
    captcha_result: Optional[bool]
    captcha_token: Optional[str]
    redirect: Optional[str]
    user: Optional[User]

    guid: Optional[str]
    telegram: Optional[str]
    email: Optional[str]
