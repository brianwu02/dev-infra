"""Obviously the best hello world app. Increments a counter in TimescaleDB on every hit."""

import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI

DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://{user}:{password}@{host}:{port}/{db}".format(
        user=os.environ.get("DB_USER", "devuser"),
        password=os.environ.get("DB_PASSWORD", "changeme"),
        host=os.environ.get("DB_HOST", "timescaledb"),
        port=os.environ.get("DB_PORT", "5432"),
        db=os.environ.get("DB_NAME", "devdb"),
    ),
)

pool: asyncpg.Pool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=3)
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS hello_counter (
            id   integer PRIMARY KEY DEFAULT 1,
            hits bigint  NOT NULL DEFAULT 0,
            CHECK (id = 1)
        )
    """)
    await pool.execute("""
        INSERT INTO hello_counter (id, hits) VALUES (1, 0)
        ON CONFLICT (id) DO NOTHING
    """)
    yield
    await pool.close()


app = FastAPI(title="obviously-the-best-hello-world-app", lifespan=lifespan)


@app.get("/")
async def root():
    row = await pool.fetchrow("SELECT hits FROM hello_counter WHERE id = 1")
    return {"message": "Hello from obviously-the-best-hello-world-app", "hits": row["hits"]}


@app.post("/hit")
async def hit():
    row = await pool.fetchrow(
        "UPDATE hello_counter SET hits = hits + 1 WHERE id = 1 RETURNING hits"
    )
    return {"message": "Obviously the best hit counter", "hits": row["hits"]}


@app.post("/reset")
async def reset():
    await pool.execute("UPDATE hello_counter SET hits = 0 WHERE id = 1")
    return {"message": "Counter reset", "hits": 0}
