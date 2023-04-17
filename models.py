from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(models.Model):
    guid = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=32, null=True, unique=True)
    description = fields.TextField(default='')
    email = fields.CharField(max_length=320, default='')
    telegram = fields.IntField(null=True)
    captcha_required = fields.BooleanField(default=False)
    captcha_key = fields.CharField(max_length=40, default='')
    captcha_secret_key = fields.CharField(max_length=40, default='')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
