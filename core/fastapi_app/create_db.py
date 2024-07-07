from core.fastapi_app.auth.database import Base,engine
import  asyncio

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await init_models()


if __name__ == '__main__':
    asyncio.run(main())