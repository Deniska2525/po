"""
Ручной запуск сидинга базы данных.

При обычной работе через docker-compose делать это НЕ нужно — app/main.py
вызывает тот же код (app/seed_core.py) автоматически при каждом старте
приложения, идемпотентно. Скрипт оставлен для ручных случаев — например,
чтобы прогнать сидинг на удалённой БД (Render) через её Shell:

    python init_db.py
"""
import os
from app.database import SessionLocal
from app.seed_core import run

print("=" * 60)
print("РУЧНОЙ ЗАПУСК СИДИНГА БАЗЫ ДАННЫХ")
print(f"🔍 DATABASE_URL: {os.getenv('DATABASE_URL', 'не задана!')[:80]}...")
print("=" * 60)

db = SessionLocal()
try:
    run(db)
finally:
    db.close()

print("Готово.")
