#!/usr/bin/env python3
"""
Генератор примеров Excel-файлов для тестирования системы.
Создает:
1. valid_animals_v1.xlsx - корректный файл (версия 1)
2. valid_animals_v2.xlsx - обновленный файл (версия 2)
3. invalid_animals.xlsx - файл с ошибками валидации
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

def create_valid_v1():
    """Создает первый валидный файл с животными."""
    data = {
        'animal_id': [101, 102, 103, 104],
        'name': ['Бобик', 'Мурка', 'Рекс', 'Барсик'],
        'species': ['Собака', 'Кошка', 'Собака', 'Кошка'],
        'breed': ['Овчарка', 'Сиамская', 'Бульдог', 'Персидская'],
        'age_years': [3, 5, 2, 4],
        'weight_kg': [25.5, 4.2, 30.0, 5.1],
        'owner_name': ['Иванов И.И.', 'Петрова А.А.', 'Сидоров В.В.', 'Кузнецова Е.Е.'],
        'registration_date': ['2023-01-15', '2022-05-20', '2023-03-10', '2022-11-01'],
        'is_vaccinated': [True, True, False, True],
        'notes': ['Активный', 'Спокойный', 'Требует дрессировки', 'Аллергия на корм']
    }
    df = pd.DataFrame(data)
    file_path = OUTPUT_DIR / "valid_animals_v1.xlsx"
    df.to_excel(file_path, index=False, sheet_name="Animals")
    print(f"✅ Создан: {file_path}")
    return file_path

def create_valid_v2():
    """Создает вторую версию файла с изменениями."""
    data = {
        'animal_id': [101, 102, 103, 104, 105],  # Добавлено новое животное
        'name': ['Бобик', 'Мурка', 'Рекс', 'Барсик', 'Шарик'],
        'species': ['Собака', 'Кошка', 'Собака', 'Кошка', 'Собака'],
        'breed': ['Овчарка', 'Сиамская', 'Бульдог', 'Персидская', 'Лабрадор'],
        'age_years': [3, 5, 2, 4, 1],  # Возраст обновлен у некоторых
        'weight_kg': [26.0, 4.2, 30.0, 5.1, 28.5],  # Бобик поправился
        'owner_name': ['Иванов И.И.', 'Петрова А.А.', 'Сидоров В.В.', 'Кузнецова Е.Е.', 'Новиков П.П.'],
        'registration_date': ['2023-01-15', '2022-05-20', '2023-03-10', '2022-11-01', '2024-01-20'],
        'is_vaccinated': [True, True, True, True, True],  # Рекс привит
        'notes': ['Активный', 'Спокойный', 'Прошел дрессировку', 'Аллергия на корм', 'Щенок']
    }
    df = pd.DataFrame(data)
    file_path = OUTPUT_DIR / "valid_animals_v2.xlsx"
    df.to_excel(file_path, index=False, sheet_name="Animals")
    print(f"✅ Создан: {file_path}")
    return file_path

def create_invalid():
    """Создает файл с различными ошибками для тестирования валидации."""
    data = {
        'animal_id': [101, '', 103, 104, 101],  # Пустой ID и дубликат
        'name': ['Бобик', 'Мурка', '', 'Барсик', 'Тузик'],  # Пустое имя
        'species': ['Собака', 'Кошка', 'Птица', 'Кошка', 'Собака'],  # Недопустимый вид 'Птица'
        'breed': ['Овчарка', 'Сиамская', 'Бульдог', 'Персидская', 'Дворняга'],
        'age_years': [3, -5, 2, 4, 150],  # Отрицательный возраст и нереальный
        'weight_kg': [25.5, 4.2, 30.0, -5.1, 28.5],  # Отрицательный вес
        'owner_name': ['Иванов И.И.', 'Петрова А.А.', 'Сидоров В.В.', '', 'Новиков П.П.'],  # Пустой владелец
        'registration_date': ['2023-01-15', 'не_дата', '2023-03-10', '2022-11-01', '2024-01-20'],  # Неверная дата
        'is_vaccinated': [True, 'да', False, True, False],  # Неверный тип (строка вместо bool)
        'notes': ['Активный', 'Спокойный', 'Требует дрессировки', 'Аллергия', '']
    }
    df = pd.DataFrame(data)
    file_path = OUTPUT_DIR / "invalid_animals.xlsx"
    df.to_excel(file_path, index=False, sheet_name="Animals")
    print(f"✅ Создан: {file_path}")
    return file_path

if __name__ == "__main__":
    print("🚀 Генерация примеров Excel-файлов...")
    create_valid_v1()
    create_valid_v2()
    create_invalid()
    print("\n📁 Файлы созданы в папке:", OUTPUT_DIR)
    print("\n💡 Как использовать:")
    print("   1. Переместите valid_animals_v1.xlsx в data/uploads/ для первого импорта")
    print("   2. Запустите: python scripts/contract_manager.py validate examples/valid_animals_v1.xlsx")
    print("   3. Попробуйте валидировать invalid_animals.xlsx чтобы увидеть отчет об ошибках")
