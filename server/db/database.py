from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine # no

# DATABASE_URL = "postgresql+asyncpg://admin:admin@db:5432/twitter_db"
DATABASE_URL = "postgresql+asyncpg://admin:admin@0.0.0.0:5432/twitter_db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

session = AsyncSessionLocal()

