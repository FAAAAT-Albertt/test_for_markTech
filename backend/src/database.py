from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float

from typing import AsyncGenerator

from src.config import DATABASE_URL


Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Respondent(Base):
    """
    Модель для таблицы 'respondent'.

    Атрибуты:
    - id: уникальный идентификатор респондента (PK).
    - date: дата, когда был записан респондент.
    - respondent_id: уникальный идентификатор респондента.
    - sex: пол респондента (1 - мужской, 2 - женский).
    - age: возраст респондента.
    - weight: вес респондента.
    """
    __tablename__ = "respondent"

    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    respondent_id = Column(Integer, nullable=False)
    sex = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор для получения асинхронной сессии базы данных.

    Используется для работы с сессиями в асинхронном контексте. Важно: сессия
    будет автоматически закрыта после завершения работы с ней.

    Возвращаемое значение:
    - AsyncSession: асинхронная сессия для работы с базой данных.
    """
    async with async_session_maker() as session:
        yield session
