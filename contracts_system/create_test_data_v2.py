"""
Создание второй версии тестового файла с изменениями.
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# Создаем тестовые данные с изменениями:
# - Добавили 2 новых животных
# - Изменили вес у Бобика
# - Удалили Кешу (птицу)

data = {
    'contract_id': ['CTR-0001', 'CTR-0002', 'CTR-0004', 'CTR-0005', 'CTR-0006', 
                    'CTR-0007', 'CTR-0008', 'CTR-0009', 'CTR-0010', 'CTR-0011', 'CTR-0012'],
    'animal_name': ['Бобик', 'Мурка', 'Хома', 'Шелдон', 'Рекс', 
                    'Барсик', 'Гоша', 'Тузик', 'Луна', 'Полкан', 'Соня'],
    'species': ['Собака', 'Кошка', 'Грызун', 'Рептилия', 'Собака', 
                'Кошка', 'Грызун', 'Собака', 'Кошка', 'Собака', 'Кошка'],
    'birth_date': [
        (datetime.now() - timedelta(days=500)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=300)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=150)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=250)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
    ],
    'weight': [25.5, 4.2, 0.5, 2.1, 18.3, 5.1, 0.3, 12.0, 3.8, 22.0, 4.5],
    'owner_name': [
        'Иванов Иван', 'Петрова Анна', 'Кузнецова Ольга', 'Смирнов Дмитрий', 
        'Попова Елена', 'Васильев Сергей', 'Соколова Мария', 'Михайлов Андрей',
        'Федорова Наталья', 'Орлов Алексей', 'Зайцева Ирина'
    ],
    'is_active': [True, True, False, True, True, False, True, True, True, True, False],
    'notes': [
        'Активная собака, увеличился вес', 'Любит играть', '', 'Черепаха', 
        'Охранник', 'Ленивый кот', '', 'Щенок', 'Котенок', 'Новая служебная собака', 'Новый котенок'
    ]
}

df = pd.DataFrame(data)

# Сохраняем в Excel
output_file = 'uploads/animals_contracts_v2.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"✅ Вторая версия файла создана: {output_file}")
print(f"📊 Строк: {len(df)}")
print(f"\nИзменения относительно v1.0.0:")
print(f"  - Удалена запись: CTR-0003 (Кеша)")
print(f"  - Добавлено записей: 2 (CTR-0011, CTR-0012)")
print(f"  - Изменены данные в некоторых записях")
