# Система управления контрактами на животных (Excel)

## 📋 Описание
Система для автоматизированной загрузки, валидации и версионного контроля Excel-файлов с данными о животных. Предназначена для аналитиков, которые готовят и обновляют данные.

## 🚀 Возможности

### ✅ Валидация данных
- **Структура**: Проверка наличия всех обязательных колонок
- **Полнота**: Контроль пустых значений в критичных полях (`animal_id`, `name`, `owner_name`)
- **Уникальность**: Проверка дубликатов идентификаторов животных
- **Типы данных**: 
  - Возраст: 0-100 лет
  - Вес: положительное число
  - Даты: формат YYYY-MM-DD
  - Булевы поля: только True/False
- **Справочники**: Проверка видов животных по списку допустимых

### 📦 Версионность
- Автоматическое присвоение версий (v1, v2, v3...)
- Хранение истории импортов с метаданными
- Фиксация хеш-суммы файла для контроля целостности
- Отслеживание количества строк и даты импорта

### 🔍 Контроль изменений
- Просмотр полной истории версий
- Сравнение версий (количество записей, хеши)
- Блокировка импорта некорректных файлов

## 📁 Структура репозитория

```
/workspace
├── scripts/
│   └── contract_manager.py    # Основной скрипт управления
├── examples/
│   ├── generate_samples.py    # Генератор тестовых файлов
│   ├── valid_animals_v1.xlsx  # Пример корректного файла (версия 1)
│   ├── valid_animals_v2.xlsx  # Пример корректного файла (версия 2)
│   └── invalid_animals.xlsx   # Пример файла с ошибками
├── data/
│   ├── uploads/               # Папка для загрузки новых файлов
│   ├── versions/              # Хранилище версий контрактов
│   └── contracts_metadata.json # База метаданных
└── README_CONTRACTS.md        # Эта документация
```

## 🛠 Использование

### 1. Показать требуемую структуру файла
```bash
python scripts/contract_manager.py schema
```

### 2. Проверить файл перед загрузкой
```bash
python scripts/contract_manager.py validate <путь_к_файлу>
```

**Пример:**
```bash
python scripts/contract_manager.py validate examples/valid_animals_v1.xlsx
```

### 3. Импортировать файл (сохранить версию)
```bash
python scripts/contract_manager.py import <путь_к_файлу>
```

**Пример:**
```bash
python scripts/contract_manager.py import examples/valid_animals_v2.xlsx
```

### 4. Посмотреть историю версий
```bash
# Все контракты
python scripts/contract_manager.py history

# Конкретный контракт
python scripts/contract_manager.py history valid_animals
```

## 📊 Требуемая структура Excel-файла

### Обязательные колонки:
| Колонка | Тип | Описание |
|---------|-----|----------|
| `animal_id` | int/string | Уникальный идентификатор животного |
| `name` | string | Кличка/имя животного |
| `species` | string | Вид животного (из справочника) |
| `breed` | string | Порода |
| `age_years` | int | Возраст в годах (0-100) |
| `weight_kg` | float | Вес в кг (>0) |
| `owner_name` | string | ФИО владельца |
| `registration_date` | date | Дата регистрации (YYYY-MM-DD) |
| `is_vaccinated` | bool | Привито ли животное (True/False) |

### Дополнительные колонки:
- `notes` - примечания (необязательно)

### Допустимые значения для `species`:
`Собака`, `Кошка`, `Птица`, `Рыба`, `Хорек`, `Кролик`

## 🎯 Сценарий работы аналитика

1. **Подготовка файла**: Аналитик заполняет Excel-файл по шаблону
2. **Предварительная проверка**: 
   ```bash
   python scripts/contract_manager.py validate my_animals.xlsx
   ```
3. **Исправление ошибок**: Если найдены ошибки, аналитик исправляет их в файле
4. **Импорт**: После успешной валидации:
   ```bash
   python scripts/contract_manager.py import my_animals.xlsx
   ```
5. **Верификация**: Проверка, что версия сохранена:
   ```bash
   python scripts/contract_manager.py history my_animals
   ```

## 🧪 Тестирование на примерах

В репозитории есть готовые примеры для тестирования:

```bash
# 1. Создать примеры (если еще не созданы)
python examples/generate_samples.py

# 2. Проверить валидный файл
python scripts/contract_manager.py validate examples/valid_animals_v1.xlsx

# 3. Проверить файл с ошибками (увидеть отчет)
python scripts/contract_manager.py validate examples/invalid_animals.xlsx

# 4. Импортировать две версии
python scripts/contract_manager.py import examples/valid_animals_v1.xlsx
python scripts/contract_manager.py import examples/valid_animals_v2.xlsx

# 5. Посмотреть историю
python scripts/contract_manager.py history
```

## 🔧 Расширение функционала

Для добавления новых правил валидации отредактируйте функцию `validate_data()` в `scripts/contract_manager.py`.

Для изменения списка допустимых видов обновите множество `VALID_SPECIES`.

## 📝 Метаданные

Все метаданные хранятся в `data/contracts_metadata.json` в формате:
```json
{
  "contract_name": {
    "created_at": "2024-01-01T10:00:00",
    "last_version": 2,
    "versions": [
      {
        "version": 1,
        "filename": "contract_v1.xlsx",
        "imported_at": "2024-01-01T10:00:00",
        "hash": "abc123...",
        "rows_count": 100
      }
    ]
  }
}
```

## ⚠️ Важные замечания

1. Файлы с ошибками валидации **не могут** быть импортированы
2. Каждая новая загрузка файла с тем же именем создает новую версию
3. Хеш-сумма позволяет отследить, изменилось ли содержимое файла
4. Система не удаляет старые версии - история сохраняется полностью
