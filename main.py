"""Запускает сервер FastAPI"""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from uvicorn import run
from uvicorn.config import LOGGING_CONFIG

import settings
from helpers import auth
from router import clean_router, secret_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(secret_router, dependencies=[Depends(auth)])
app.include_router(clean_router)

if settings.DEBUG:
    app.mount("/static", StaticFiles(directory="static"), name="static")

# register_tortoise(
#     app,
#     db_url=settings.DB_URL,
#     modules={"models": ["models"]},
#     generate_schemas=False,
#     add_exception_handlers=False,
# )

@app.on_event("startup")
async def startup_event():
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = \
        '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    register_tortoise(app, config=settings.TORTOISE_ORM, generate_schemas=False)


if __name__ == "__main__":
    run(app, host=settings.HOST, port=settings.PORT)
