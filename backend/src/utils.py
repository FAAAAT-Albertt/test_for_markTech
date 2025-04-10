from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

import csv

from src.database import Respondent as respondent

CSV_PATH = "templates/data_1.csv"
BATCH_SIZE = 1000

async def load_csv_to_db(session: AsyncSession) -> None:
    """
    Загружает данные из CSV файла в таблицу базы данных.

    Эта функция читает CSV файл с данными респондентов, преобразует их в словари
    и вставляет их в таблицу `respondent` в базе данных. Вставка выполняется пакетами
    по размеру, указанному в BATCH_SIZE. После каждой вставки выполняется commit.

    Параметры:
    - session (AsyncSession): асинхронная сессия для работы с базой данных.

    Возвращаемое значение:
    - None: Функция не возвращает значений, она изменяет состояние базы данных.

    Примечания:
    - CSV файл должен быть в формате с разделителем `;` и содержать столбцы:
      "Date", "respondent", "Sex", "Age", "Weight".
    - Вставка данных выполняется пакетами по BATCH_SIZE, что позволяет оптимизировать
      работу с большим количеством данных.
    """
    with open(CSV_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")
        batch = []

        for row in reader:
            batch.append({
                "date": row["Date"],
                "respondent_id": int(row["respondent"]),
                "sex": int(row["Sex"]),
                "age": int(row["Age"]),
                "weight": float(row["Weight"])
            })

            if len(batch) >= BATCH_SIZE:
                await session.execute(insert(respondent), batch)
                await session.commit()
                batch.clear()


        if batch:
            await session.execute(insert(respondent), batch)
            await session.commit()
