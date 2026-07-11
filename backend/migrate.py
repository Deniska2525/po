"""
Разовый скрипт для безопасного добавления новых колонок в уже существующую БД.

Base.metadata.create_all() (используется в main.py) создаёт только отсутствующие
таблицы — он НЕ добавляет новые колонки в уже существующие таблицы. Поэтому при
любом изменении модели (добавили Column) нужно либо использовать полноценный
инструмент миграций (рекомендуется Alembic, см. комментарий внизу файла),
либо — для простых случаев — прогнать такой ALTER TABLE вручную.

Запуск (локально или через Render Shell):
    python migrate.py
Скрипт идемпотентен — можно запускать сколько угодно раз, IF NOT EXISTS не даст
упасть, если колонка уже есть.
"""
from sqlalchemy import text
from app.database import engine

MIGRATIONS = [
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS tags VARCHAR;",
]

def run():
    with engine.begin() as conn:
        for sql in MIGRATIONS:
            print(f"Выполняю: {sql}")
            conn.execute(text(sql))
    print("✅ Миграция завершена")

if __name__ == "__main__":
    run()

# ПРИМЕЧАНИЕ ПРО БУДУЩЕЕ:
# Если проект будет расти, стоит подключить Alembic (pip install alembic) —
# он сам генерирует такие ALTER TABLE по diff'у модели и БД, и не нужно будет
# вручную писать миграции при каждом изменении models.py.
