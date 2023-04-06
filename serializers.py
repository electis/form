from typing import Optional

from pydantic import BaseModel


class BaseResult(BaseModel):
    """Основной ответ сервиса"""
    result: Optional[str]


class Client(BaseModel):
    ip: Optional[str]
    origin: str
    telegram: Optional[str]
    email: Optional[str]
    redirect: str
