"""Надстройки, расширяющие функционал моделей"""
from fastapi_mail import FastMail, MessageSchema, MessageType
import httpx
import settings
from serializers import Client


class Inform:

    def __init__(self, data: dict, client: Client = None):
        self.data = data
        self.client = client

    @staticmethod
    async def send_tg(text, tg_id=None):
        tg_id = tg_id or settings.INFORM_TG_ID
        url = f"https://api.telegram.org/bot{settings.INFORM_TG_TOKEN}/sendMessage" \
              f"?chat_id={tg_id}&parse_mode=Markdown&text={text}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.text

    @staticmethod
    async def send_email(text, email):
        message = MessageSchema(
            subject="Info",
            recipients=[email],
            body=text,
            subtype=MessageType.plain
        )
        fm = FastMail(settings.MAIL_CONFIG)
        await fm.send_message(message)

    def make_text(self):
        text = f"-- client\n" \
               f"ip: {self.client.ip}\n" \
               f"origin: {self.client.origin}\n" \
               f"-- data\n"
        for key, value in self.data.items():
            text += f"{key}: {value}\n"
        return text

    async def inform(self):
        text = self.make_text()

        if settings.INFORM_TG_TOKEN and self.client.telegram:
            try:
                await self.send_tg(text, self.client.telegram)
            except Exception as exc:
                print(exc)

        if self.client.email:
            try:
                await self.send_email(text, self.client.email)
            except Exception as exc:
                print(exc)
