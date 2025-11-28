import pandas as pd
from sqlalchemy import create_engine
import sqlite3 # Можно использовать только sqlite3, но sqlalchemy упрощает работу с to_sql

# --- 1. Данные для записи ---
data = [
    {"id": 1, "name": "Anycubic Kobra 2 Pro", "cost": 33900},
    {"id": 2, "name": "Bambu Lab P1S Combo", "cost": 99999},
    {"id": 3, "name": "Creality Ender-3 V3 SE", "cost": 17300},
    {"id": 4, "name": "Elegoo Neptune 4 Pro", "cost": 37000},
    {"id": 5, "name": "FlashForge Adventurer 5M Pro", "cost": 63000},
    {"id": 6, "name": "Anycubic Kobra 2 Max", "cost": 59900},
    {"id": 7, "name": "QIDI Q1 Pro", "cost": 79900},
    {"id": 8, "name": "Creality K1 Max", "cost": 87790},
    {"id": 9, "name": "Bambu Lab A1 Mini Combo", "cost": 36999},
    {"id": 10, "name": "FLSUN S1 Pro", "cost": 199000}
]

df = pd.DataFrame(data)

# --- 2. Параметры базы данных и таблицы ---
DATABASE_FILE = 'database.db' # Имя вашего файла базы данных
TABLE_NAME = 'products'       # Имя целевой таблицы (согласно вашей схеме)

# --- 3. Подключение и запись данных ---
try:
    # Создание "движка" SQLAlchemy для подключения к SQLite
    # 'sqlite:///' указывает на локальный файл
    engine = create_engine(f'sqlite:///{DATABASE_FILE}')

    # Запись данных в таблицу 'products'
    # if_exists='replace': удаляет старую таблицу и создает новую с этими данными
    # index=False: не записывать индекс DataFrame как отдельный столбец
    df.to_sql(TABLE_NAME, con=engine, if_exists='replace', index=False)

    print(f"✅ Успешно записано {len(df)} товаров в таблицу '{TABLE_NAME}' в базе данных '{DATABASE_FILE}'.")
    
except Exception as e:
    print(f"❌ Произошла ошибка при записи в базу данных: {e}")
finally:
    # Закрытие соединения с БД
    if 'engine' in locals():
        engine.dispose()


# --- 4. Проверка (Чтение данных для подтверждения) ---
print("\n--- Проверка (Чтение из БД) ---")
try:
    conn = sqlite3.connect(DATABASE_FILE)
    
    # Чтение данных из таблицы 'products' обратно в DataFrame
    df_check = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    
    print(f"Количество записей, прочитанных из таблицы '{TABLE_NAME}': {len(df_check)}")
    print("\nПервые 5 записей в таблице 'products':")
    print(df_check.head())
    
except Exception as e:
    print(f"❌ Ошибка при проверке чтения из БД: {e}")
finally:
    if 'conn' in locals():
        conn.close()