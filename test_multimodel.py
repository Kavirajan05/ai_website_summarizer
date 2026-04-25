import asyncio
from app.services.multimodel_service import run_multimodel_pipeline

async def test():
    res = await run_multimodel_pipeline("what is java")
    print("Result:", res)

if __name__ == "__main__":
    asyncio.run(test())
