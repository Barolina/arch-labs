#!/usr/bin/env python3
"""
Система управления контрактами на животных (Excel).
Обеспечивает валидацию, версионность и контроль изменений.

Команды:
    validate <file>           - Проверить файл на ошибки
    import <file>             - Импортировать файл (сохранить версию)
    history [contract_name]   - Показать историю версий
    diff <v1> <v2>            - Сравнить две версии
    schema                    - Показать требуемую структуру файла
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook

# Конфигурация
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
VERSIONS_DIR = DATA_DIR / "versions"
METADATA_FILE = DATA_DIR / "contracts_metadata.json"

# Правила валидации
REQUIRED_COLUMNS = [
    'animal_id', 'name', 'species', 'breed', 
    'age_years', 'weight_kg', 'owner_name', 
    'registration_date', 'is_vaccinated'
]

VALID_SPECIES = {'Собака', 'Кошка', 'Птица', 'Рыба', 'Хорек', 'Кролик'}

def get_file_hash(filepath):
    """Вычисляет MD5 хеш файла для контроля целостности."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def load_metadata():
    """Загружает метаданные всех контрактов."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    """Сохраняет метаданные."""
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def validate_schema(df):
    """Проверяет наличие всех обязательных колонок."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        return False, f"Отсутствуют колонки: {missing}"
    return True, "OK"

def validate_data(df):
    """Глубокая валидация данных."""
    errors = []
    
    # 1. Проверка пустых значений в обязательных полях
    for col in ['animal_id', 'name', 'owner_name']:
        empty_count = df[col].isna().sum() + (df[col].astype(str).str.strip() == '').sum()
        if empty_count > 0:
            errors.append(f"Колонка '{col}': найдено {empty_count} пустых значений")
    
    # 2. Уникальность animal_id
    if 'animal_id' in df.columns:
        ids = df['animal_id'].dropna().astype(str).str.strip()
        duplicates = ids[ids.duplicated()]
        if not duplicates.empty:
            errors.append(f"Дубликаты animal_id: {duplicates.tolist()}")
    
    # 3. Типы данных и диапазоны
    if 'age_years' in df.columns:
        try:
            ages = pd.to_numeric(df['age_years'], errors='coerce')
            invalid = ages[(ages < 0) | (ages > 100)]
            if not invalid.empty:
                errors.append(f"Некорректный возраст (0-100): строки {invalid.index.tolist()}")
        except Exception:
            errors.append("Колонка 'age_years' содержит нечисловые значения")
    
    if 'weight_kg' in df.columns:
        try:
            weights = pd.to_numeric(df['weight_kg'], errors='coerce')
            invalid = weights[weights <= 0]
            if not invalid.empty:
                errors.append(f"Некорректный вес (>0): строки {invalid.index.tolist()}")
        except Exception:
            errors.append("Колонка 'weight_kg' содержит нечисловые значения")
    
    # 4. Справочники (Species)
    if 'species' in df.columns:
        invalid_species = df[~df['species'].isin(VALID_SPECIES)]['species'].unique()
        if len(invalid_species) > 0:
            errors.append(f"Недопустимые виды: {invalid_species}. Разрешено: {VALID_SPECIES}")
    
    # 5. Формат даты
    if 'registration_date' in df.columns:
        def try_parse(d):
            try:
                pd.to_datetime(d)
                return True
            except:
                return False
        
        invalid_dates = df[~df['registration_date'].apply(try_parse)]
        if not invalid_dates.empty:
            errors.append(f"Некорректные даты: строки {invalid_dates.index.tolist()}")
    
    # 6. Булево поле
    if 'is_vaccinated' in df.columns:
        non_bool = df[~df['is_vaccinated'].apply(lambda x: isinstance(x, bool))]
        if not non_bool.empty:
            errors.append(f"Поле 'is_vaccinated' должно быть True/False, найдены другие типы в строках {non_bool.index.tolist()}")
    
    is_valid = len(errors) == 0
    return is_valid, "\n".join(errors) if errors else "Все проверки пройдены"

def cmd_validate(filepath):
    """Команда: Валидация файла."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Файл не найден: {path}")
        return False
    
    print(f"🔍 Валидация файла: {path.name}")
    print("-" * 40)
    
    try:
        df = pd.read_excel(path)
    except Exception as e:
        print(f"❌ Ошибка чтения Excel: {e}")
        return False
    
    print(f"📊 Строк: {len(df)}, Колонок: {len(df.columns)}")
    
    # Проверка схемы
    schema_ok, schema_msg = validate_schema(df)
    if not schema_ok:
        print(f"❌ Структура: {schema_msg}")
        return False
    print("✅ Структура файла корректна")
    
    # Проверка данных
    data_ok, data_msg = validate_data(df)
    if data_ok:
        print("✅ Данные корректны")
        print("\n🎉 Файл готов к импорту!")
        return True
    else:
        print("❌ Ошибки в данных:")
        for line in data_msg.split('\n'):
            print(f"   - {line}")
        return False

def cmd_import(filepath):
    """Команда: Импорт файла с сохранением версии."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Файл не найден: {path}")
        return False
    
    # Сначала валидация
    if not cmd_validate(filepath):
        print("\n⛔ Импорт отклонен из-за ошибок валидации.")
        return False
    
    df = pd.read_excel(path)
    file_hash = get_file_hash(path)
    
    # Определяем имя контракта (по имени файла без версии)
    contract_name = path.stem.split('_v')[0] if '_v' in path.stem else path.stem
    
    metadata = load_metadata()
    
    if contract_name not in metadata:
        metadata[contract_name] = {
            'created_at': datetime.now().isoformat(),
            'versions': []
        }
    
    version_num = len(metadata[contract_name]['versions']) + 1
    version_filename = f"{contract_name}_v{version_num}.xlsx"
    
    # Сохранение версии
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = VERSIONS_DIR / version_filename
    
    # Копируем файл
    df.to_excel(dest_path, index=False)
    
    # Запись метаданных
    version_info = {
        'version': version_num,
        'filename': version_filename,
        'source_file': str(path),
        'imported_at': datetime.now().isoformat(),
        'hash': file_hash,
        'rows_count': len(df),
        'imported_by': 'analyst' # В будущем можно брать из ОС
    }
    
    metadata[contract_name]['versions'].append(version_info)
    metadata[contract_name]['last_version'] = version_num
    save_metadata(metadata)
    
    print(f"\n✅ Импорт успешен!")
    print(f"   Контракт: {contract_name}")
    print(f"   Версия: {version_num}")
    print(f"   Сохранено в: {dest_path}")
    return True

def cmd_history(contract_name=None):
    """Команда: Показать историю."""
    metadata = load_metadata()
    
    if not metadata:
        print("📭 История пуста. Еще не было импортов.")
        return
    
    if contract_name:
        if contract_name not in metadata:
            print(f"❌ Контракт '{contract_name}' не найден.")
            return
        contracts_to_show = {contract_name: metadata[contract_name]}
    else:
        contracts_to_show = metadata
    
    print("📜 История версий контрактов:\n")
    for name, info in contracts_to_show.items():
        print(f"📦 {name}")
        print(f"   Создан: {info['created_at'][:10]}")
        print(f"   Версий: {info.get('last_version', 0)}")
        for v in info['versions']:
            print(f"      v{v['version']} | {v['imported_at'][:10]} | строк: {v['rows_count']} | hash: {v['hash'][:8]}...")
        print()

def cmd_schema():
    """Команда: Показать схему."""
    print("📋 Требуемая структура Excel файла:\n")
    print("Обязательные колонки:")
    for col in REQUIRED_COLUMNS:
        print(f"  - {col}")
    
    print(f"\nДопустимые значения для 'species': {', '.join(VALID_SPECIES)}")
    print("\nПравила:")
    print("  - animal_id: уникальное число или строка, не пусто")
    print("  - age_years: число от 0 до 100")
    print("  - weight_kg: положительное число")
    print("  - registration_date: формат YYYY-MM-DD")
    print("  - is_vaccinated: True/False (булево)")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'validate':
        if len(sys.argv) < 3:
            print("❌ Укажите путь к файлу: contract_manager.py validate <file>")
            sys.exit(1)
        success = cmd_validate(sys.argv[2])
        sys.exit(0 if success else 1)
        
    elif command == 'import':
        if len(sys.argv) < 3:
            print("❌ Укажите путь к файлу: contract_manager.py import <file>")
            sys.exit(1)
        success = cmd_import(sys.argv[2])
        sys.exit(0 if success else 1)
        
    elif command == 'history':
        contract = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_history(contract)
        
    elif command == 'schema':
        cmd_schema()
        
    else:
        print(f"❌ Неизвестная команда: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
