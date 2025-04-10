from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List, Tuple

from src.database import Respondent


async def get_avg_weight(
    session: AsyncSession, filter_text: str
) -> List[Tuple[int, float]]:
    """
    Получает средний вес респондентов, соответствующих заданным фильтрам.

    Эта функция выполняет SQL-запрос для расчета среднего значения веса (avg(weight))
    для респондентов, которые удовлетворяют условию фильтра. Результат группируется по
    уникальному идентификатору респондента.

    Параметры:
    - session (AsyncSession): асинхронная сессия для работы с базой данных.
    - filter_text (str): строка фильтра, представляющая SQL-синтаксис (например, "age > 18").

    Возвращаемое значение:
    - list: Список кортежей, где каждый кортеж содержит уникальный идентификатор респондента
      и среднее значение веса (avg_weight).
    """
    filter_text = filter_text.lower()

    query = (
        select(
            Respondent.respondent_id, func.avg(Respondent.weight).label("avg_weight")
        ).filter(text(filter_text))
    ).group_by(Respondent.respondent_id)

    result = await session.execute(query)
    return result.fetchall()
