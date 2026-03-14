"""Obviously the best hello world app. Increments a counter in TimescaleDB on every hit."""

import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

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

PAGE = """<!DOCTYPE html>
<html>
<head>
  <title>obviously-the-best-hello-world-app</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; height: 100vh; display: flex;
           align-items: center; justify-content: center; background: #111; color: #fff; }
    .card { text-align: center; }
    h1 { font-size: 1.2rem; font-weight: 400; color: #888; margin-bottom: 2rem; }
    #count { font-size: 8rem; font-weight: 700; margin-bottom: 2rem;
             font-variant-numeric: tabular-nums; }
    .buttons { display: flex; gap: 1rem; justify-content: center; }
    button { font-size: 1.1rem; padding: 0.75rem 2rem; border: 1px solid #333;
             border-radius: 8px; background: #1a1a1a; color: #fff; cursor: pointer;
             transition: background 0.15s; }
    button:hover { background: #2a2a2a; }
    button:active { background: #333; }
    .hit { background: #1a3a1a; border-color: #2a5a2a; }
    .hit:hover { background: #2a4a2a; }
    .reset { background: #3a1a1a; border-color: #5a2a2a; }
    .reset:hover { background: #4a2a2a; }
  </style>
</head>
<body>
  <div class="card">
    <h1>obviously-the-best-hello-world-app</h1>
    <div id="count">0</div>
    <div class="buttons">
      <button class="hit" onclick="hit()">Hit</button>
      <button class="reset" onclick="reset()">Reset</button>
    </div>
  </div>
  <script>
    async function load() {
      const r = await fetch('/api');
      const d = await r.json();
      document.getElementById('count').textContent = d.hits;
    }
    async function hit() {
      const r = await fetch('/api/hit', { method: 'POST' });
      const d = await r.json();
      document.getElementById('count').textContent = d.hits;
    }
    async function reset() {
      const r = await fetch('/api/reset', { method: 'POST' });
      const d = await r.json();
      document.getElementById('count').textContent = d.hits;
    }
    load();
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return PAGE


@app.get("/api")
async def read():
    row = await pool.fetchrow("SELECT hits FROM hello_counter WHERE id = 1")
    return {"hits": row["hits"]}


@app.post("/api/hit")
async def hit():
    row = await pool.fetchrow(
        "UPDATE hello_counter SET hits = hits + 1 WHERE id = 1 RETURNING hits"
    )
    return {"hits": row["hits"]}


@app.post("/api/reset")
async def reset():
    await pool.execute("UPDATE hello_counter SET hits = 0 WHERE id = 1")
    return {"hits": 0}
