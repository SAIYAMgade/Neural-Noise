import sys
sys.path.insert(0, ".")
import asyncio
from api.database import get_db_manager
from sqlalchemy import select
from api.models import AgentExecutionTrace

async def check():
    mgr = get_db_manager()
    async with mgr.session() as s:
        res = (await s.execute(select(AgentExecutionTrace))).scalars().all()
        print(f"Total traces found: {len(res)}")
        for r in res:
            print(f"- {r.id}: {r.workflow_type} | Latency: {r.total_latency_ms} | Steps: {len(r.steps) if r.steps else 0}")
            if r.steps:
                print("  Sample step:", r.steps[0])

if __name__ == "__main__":
    asyncio.run(check())
