from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "guid" CHAR(36) NOT NULL  PRIMARY KEY,
    "telegram" INT  UNIQUE,
    "description" TEXT NOT NULL,
    "email" VARCHAR(320) NOT NULL  DEFAULT '',
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "sites" (
    "guid" CHAR(36) NOT NULL  PRIMARY KEY,
    "domain" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "email" VARCHAR(320) NOT NULL  DEFAULT '',
    "redirect" VARCHAR(255) NOT NULL  DEFAULT '',
    "captcha_required" INT NOT NULL  DEFAULT 0,
    "captcha_key" VARCHAR(40) NOT NULL  DEFAULT '',
    "captcha_secret_key" VARCHAR(40) NOT NULL  DEFAULT '',
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("guid") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
