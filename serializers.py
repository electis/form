from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from models import Users

User = pydantic_model_creator(Users, name="User")


class BaseResult(BaseModel):
    """Основной ответ сервиса"""
    result: Optional[str]


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
