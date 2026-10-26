import asyncio
import os
from sqlalchemy import text
from api.database import DatabaseManager

os.environ['DATABASE_URL'] = 'postgresql+asyncpg://postgres:postgres@localhost:5432/finpilot'

async def check():
    mgr = DatabaseManager()
    async with mgr.session() as s:
        res = await s.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"))
        count = res.scalar()
        print(f"Total public tables in finpilot: {count}")

        res = await s.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
        tables = [r[0] for r in res.fetchall()]
        print("Tables:", tables)

asyncio.run(check())
