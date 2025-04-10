from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.database import Respondent as respondent
from src.utils import load_csv_to_db
from src.decorators import run_if_table_empty
from src.crud import get_avg_weight

app = FastAPI()


@app.get(
    "/load-data-into-database",
)
@run_if_table_empty(respondent)
async def load_data_if_empty(session: AsyncSession = Depends(get_async_session)):
    """
    Загрузка данных из CSV в таблицу, если она пуста.
    
    Этот эндпоинт проверяет, если таблица пуста, загружает данные из CSV в базу данных.
    
    Параметры:
    - session (AsyncSession): асинхронная сессия для работы с базой данных.
    
    Возвращаемое значение:
    - Успешная загрузка данных в базу данных.
    """
    await load_csv_to_db(session)


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
        raise HTTPException(status_code=404, detail="Audiences do not overlap")

    total_weight_audience1 = sum(audience1_dct_data.values())
    total_weight_intersection = sum(audience2_dct_data[resp_id] for resp_id in intersection)

    if total_weight_audience1 == 0:
        raise HTTPException(status_code=400, detail="No respondents found in audience1")

    percent = total_weight_intersection / total_weight_audience1
    return {"percent": round(percent, 3)}