import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine)

from database.models import Base

import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv(find_dotenv())


class Database:
    def __init__(self):
        self.__engine = create_async_engine(os.getenv('DB_URL'), echo=True)
        self.__session_maker = async_sessionmaker(bind=self.__engine, class_=AsyncSession, expire_on_commit=False)

    async def create_db(self):
        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db(self):
        async with self.__engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @property
    def session_maker(self):
        return self.__session_maker
