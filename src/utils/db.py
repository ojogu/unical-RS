from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import config
from src.v1.base.model import Base
from src.v1.model import *
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager

from src.utils.log import setup_logger
logger = setup_logger(__name__, file_path="db.log")

# Create async engine
engine = create_async_engine(
    url=config.DATABASE_URL,
    # echo=settings.debug,
    poolclass=NullPool,  # Use NullPool for async operations
    future=True,
)


async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)



@asynccontextmanager
#this helps in a way that, each internal async function in the bg task gets a new session, which prevent event loop or connection issue, coupled with the poolclass=NullPool param when creating the engine, it opens a new connection 
async def get_async_db_session():
    """
    Get an async database session for use in background tasks.

    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# # Create async session factory
# AsyncSessionLocal = async_sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()



async def init_db():
    """
    Initialize the database by creating all tables defined in the Base metadata.

    This asynchronous function uses the SQLAlchemy engine to create all tables
    that are defined in the Base metadata. It's typically used when setting up
    the database for the first time or after a complete reset.

    The function uses a connection from the engine and runs the create_all
    method synchronously within the asynchronous context.
    """
    try:
        async with engine.begin() as conn:
            # Use run_sync to call the synchronous create_all method in an async context
            await conn.run_sync(Base.metadata.create_all)
            print(Base.metadata.tables.keys())
    except SQLAlchemyError as e:
        logger.error(f"error creating the db: {e}")


async def drop_db():
    """
    Drop all tables in the database.

    This asynchronous function uses the SQLAlchemy engine to drop all tables
    that are defined in the Base metadata. It's typically used when you want
    to completely reset the database structure.

    Caution: This operation will delete all data in the tables. Use with care.
    """
    async with engine.begin() as conn:
        # Use run_sync to call the synchronous drop_all method in an async context
        await conn.run_sync(Base.metadata.drop_all)
