from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from web.app.settings import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER

DATABASE_URL = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
)


# an Engine, which the Session will use for connection
# resources
engine = create_async_engine(DATABASE_URL, future=True, echo=False)

async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
)

Base = declarative_base()


async def get_db():
    """Yields async SessionLocal instance for FastAPI resources.
    Finally, closes connection to database.
    :return: Iterator that yields SessionLocal instance.
    """
    # we can now construct a Session() without needing to pass the
    # engine each time
    async with async_session() as session:
        yield session
    # closes the session
