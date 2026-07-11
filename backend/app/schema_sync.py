"""
Безопасная авто-синхронизация схемы БД.

Base.metadata.create_all() создаёт только отсутствующие ТАБЛИЦЫ, но не умеет
добавлять новые КОЛОНКИ в уже существующие таблицы. На бесплатном плане Render
нет доступа к Shell, чтобы вручную прогнать ALTER TABLE — поэтому эта функция
делает то же самое автоматически при каждом старте приложения:

  1. Смотрит, какие колонки реально есть в каждой таблице БД.
  2. Сравнивает со списком колонок в моделях (models.py).
  3. Для каждой недостающей колонки выполняет ALTER TABLE ... ADD COLUMN.

Важно, чего эта функция НИКОГДА не делает:
  - не удаляет колонки/таблицы;
  - не меняет тип существующих колонок;
  - не трогает существующие данные.
Это строго аддитивная, идемпотентная операция — безопасно гонять на каждом
старте, в проде, без даунтайма и без риска потерять данные.

Ограничение: новую колонку добавляем как nullable, даже если в модели она
указана как non-nullable — так и должно быть, потому что у уже существующих
строк для неё нет значения. Если нужно NOT NULL с реальными данными —
это уже полноценная миграция (см. Alembic) с ручным заполнением значений.

Для более сложных изменений схемы (переименование колонки, смена типа,
объединение таблиц и т.п.) этот механизм не подходит — тогда нужен Alembic.
"""
from sqlalchemy import inspect, text


def sync_schema(engine, Base):
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table_name, table in Base.metadata.tables.items():
            if table_name not in existing_tables:
                # Таблицы целиком уже создаёт create_all(), тут делать нечего
                continue

            existing_columns = {col["name"] for col in inspector.get_columns(table_name)}

            for column in table.columns:
                if column.name in existing_columns:
                    continue

                col_type = column.type.compile(dialect=engine.dialect)
                ddl = f'ALTER TABLE {table_name} ADD COLUMN "{column.name}" {col_type}'
                print(f"🔧 [schema_sync] Добавляю колонку {table_name}.{column.name} ({col_type})")
                conn.execute(text(ddl))
