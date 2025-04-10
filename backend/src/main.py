from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session, async_session_maker
from src.utils import load_csv_to_db
from src.crud import get_avg_weight


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_maker() as session:
        await load_csv_to_db(session)
    yield


app = FastAPI(lifespan=lifespan)

@app.get(
    "/get-percent",
)
async def get_result_percient(
    audience1: str,
    audience2: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Рассчитывает процент вхождения второй аудитории в первую на основе среднего веса респондентов.
    
    Параметры:
    - audience1 (str): Условия для фильтрации респондентов первой аудитории в формате SQL.
    - audience2 (str): Условия для фильтрации респондентов второй аудитории в формате SQL.
    - session (AsyncSession): асинхронная сессия для работы с базой данных.
    
    Возвращаемое значение:
    - { "percent": результат } - процент пересечения второй аудитории в первой на основе среднего веса.
    
    Исключения:
    - 404 - Если аудитории не пересекаются.
    - 400 - Если в первой аудитории нет респондентов.
    """
    avg_weight_aud1 = await get_avg_weight(session, filter_text=audience1)
    avg_weight_aud2 = await get_avg_weight(session, filter_text=audience2)

    audience1_dct_data = {row[0]: row[1] for row in avg_weight_aud1}
    audience2_dct_data = {row[0]: row[1] for row in avg_weight_aud2}

    intersection = set(audience1_dct_data.keys()).intersection(set(audience2_dct_data.keys()))

    if not intersection:
        return {"percent": 0}
    
    total_weight_audience1 = sum(audience1_dct_data.values())
    total_weight_intersection = sum(audience2_dct_data[resp_id] for resp_id in intersection)

    if total_weight_audience1 == 0:
       return {"percent": 0}

    percent = total_weight_intersection / total_weight_audience1
    return {"percent": round(percent, 3)}