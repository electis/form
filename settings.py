"""Основные настройки проекта, берутся из .env файла"""
import os

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv('.env.example')
load_dotenv(override=True)

PORT = int(os.getenv('PORT', '8000'))
HOST = os.getenv('HOST', '0.0.0.0')

SECRET_TOKEN = os.getenv('SECRET_TOKEN')
ENVIRONMENT = os.getenv('ENVIRONMENT')
DEBUG = True
if ENVIRONMENT == 'production':
    assert SECRET_TOKEN != 'very_secret_token', 'Token not secure'
    DEBUG = False

DB_URL = os.getenv('DB_URL')

INFORM_TG_TOKEN = os.getenv('INFORM_TG_TOKEN')
INFORM_TG_ID = os.getenv('INFORM_TG_ID')

MAIL_CONFIG = ConnectionConfig(
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_USERNAME=os.getenv('MAIL_FROM'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.mail.ru",
    MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)

TORTOISE_ORM = {
    "connections": {
        "default": DB_URL,
    },
    "apps": {
        "default": {
            "models": [
                "models", "aerich.models",
            ],
            "default_connection": "default",
        },
    }
}
