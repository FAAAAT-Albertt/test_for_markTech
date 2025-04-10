from functools import wraps
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def run_if_table_empty(model):
    """
    Декоратор для выполнения функции только в случае, если таблица модели пуста.

    Используется для инициализационной логики, например, загрузки данных в базу данных,
    которая должна выполняться только один раз — если в таблице ещё нет данных.

    Функция не будет вызвана, если в таблице уже есть хотя бы одна запись.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(session: AsyncSession, *args, **kwargs):
            result = await session.execute(select(model).limit(10))
            if result.scalars().first() is None:
                return await func(session, *args, **kwargs)

        return wrapper
    return decorator