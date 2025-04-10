from functools import wraps
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Any


def run_if_table_empty(table: Any) -> Callable:
    """
    Декоратор для проверки, пуста ли таблица, перед выполнением функции.

    Этот декоратор выполняет проверку на наличие данных в указанной таблице. Если таблица пуста,
    функция будет выполнена, иначе будет выброшено исключение с ошибкой, что таблица уже содержит данные.

    Параметры:
    - table (Any): Таблица SQLAlchemy, которую нужно проверить на наличие данных.

    Возвращает:
    - Callable: Функция, которая будет вызываться, если таблица пуста.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
            """
            Вспомогательная функция для выполнения основной логики декоратора.
            
            Эта функция проверяет, есть ли данные в таблице, и если данных нет,
            выполняет декорируемую функцию. Если данные есть, выбрасывается исключение.

            Параметры:
            - *args: Аргументы, переданные в декорируемую функцию.
            - **kwargs: Ключевые аргументы, переданные в декорируемую функцию.

            Возвращает:
            - JSONResponse: Ответ с сообщением о загрузке данных или ошибке.
            """
            session: AsyncSession = kwargs.get("session")
            if session is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session must be provided as keyword argument",
                )

            result = await session.execute(select(table).limit(10))
            total_rows = result.scalar()

            if total_rows is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Table already contains data. Cannot load more data.",
                )

            await func(*args, **kwargs)
            return JSONResponse(
                content={"message": "Table loaded successfully."},
                status_code=status.HTTP_201_CREATED
            )

        return wrapper

    return decorator
