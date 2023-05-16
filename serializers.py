from typing import Optional

from pydantic import BaseModel
from pydantic.schema import UUID
from tortoise.contrib.pydantic import pydantic_model_creator

from models import Sites, Users

User = pydantic_model_creator(Users, name="User")
Site = pydantic_model_creator(Sites, name="Site")


class BaseResult(BaseModel):
    """Основной ответ сервиса"""
    result: Optional[str]


class Client(BaseModel):
    ip: Optional[str]
    origin: Optional[str]
    captcha_result: Optional[bool]
    captcha_token: Optional[str]
    # redirect: Optional[str]
    site: Optional[Site]

    guid: UUID
    telegram: Optional[str]
    email: Optional[str]
