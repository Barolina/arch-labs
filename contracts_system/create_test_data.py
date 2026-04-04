"""
Создание тестового Excel файла для демонстрации работы системы.
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# Создаем тестовые данные
data = {
    'contract_id': [f'CTR-{i:04d}' for i in range(1, 11)],
    'animal_name': ['Бобик', 'Мурка', 'Кеша', 'Хома', 'Шелдон', 'Рекс', 'Барсик', 'Гоша', 'Тузик', 'Луна'],
    'species': ['Собака', 'Кошка', 'Птица', 'Грызун', 'Рептилия', 'Собака', 'Кошка', 'Грызун', 'Собака', 'Кошка'],
    'birth_date': [(datetime.now() - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d') for _ in range(10)],
    'weight': [random.uniform(2, 30) for _ in range(10)],
    'owner_name': [
        'Иванов Иван', 'Петрова Анна', 'Сидоров Петр', 'Кузнецова Ольга', 
        'Смирнов Дмитрий', 'Попова Елена', 'Васильев Сергей', 'Соколова Мария',
        'Михайлов Андрей', 'Федорова Наталья'
    ],
    'is_active': [True, True, True, False, True, True, False, True, True, True],
    'notes': ['Активная собака', 'Любит играть', 'Разговаривает', '', 'Черепаха', 
              'Охранник', 'Ленивый кот', '', 'Щенок', 'Котенок']
}

df = pd.DataFrame(data)

# Сохраняем в Excel
output_file = 'uploads/animals_contracts_v1.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"✅ Тестовый файл создан: {output_file}")
print(f"📊 Строк: {len(df)}")
print(f"📋 Колонки: {', '.join(df.columns)}")
