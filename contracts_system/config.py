"""
Конфигурация системы управления контрактами.
Здесь задаются правила валидации и структура файлов.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DataType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    BOOLEAN = "boolean"

class ColumnRule(BaseModel):
    name: str
    dtype: DataType
    required: bool = True
    unique: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None  # Для справочников
    description: str = ""

# Конфигурация обязательных колонок для файла с животными
ANIMAL_CONTRACT_COLUMNS = [
    ColumnRule(
        name="contract_id",
        dtype=DataType.STRING,
        required=True,
        unique=True,
        description="Уникальный идентификатор контракта"
    ),
    ColumnRule(
        name="animal_name",
        dtype=DataType.STRING,
        required=True,
        min_length=1,
        max_length=100,
        description="Кличка или название животного"
    ),
    ColumnRule(
        name="species",
        dtype=DataType.STRING,
        required=True,
        allowed_values=["Собака", "Кошка", "Птица", "Грызун", "Рептилия", "Другое"],
        description="Вид животного"
    ),
    ColumnRule(
        name="birth_date",
        dtype=DataType.DATE,
        required=True,
        description="Дата рождения (формат ГГГГ-ММ-ДД)"
    ),
    ColumnRule(
        name="weight",
        dtype=DataType.FLOAT,
        required=False,
        description="Вес в кг"
    ),
    ColumnRule(
        name="owner_name",
        dtype=DataType.STRING,
        required=True,
        description="ФИО владельца"
    ),
    ColumnRule(
        name="is_active",
        dtype=DataType.BOOLEAN,
        required=True,
        description="Активен ли контракт (True/False)"
    ),
    ColumnRule(
        name="notes",
        dtype=DataType.STRING,
        required=False,
        description="Примечания"
    )
]

class SystemConfig(BaseModel):
    upload_dir: str = "uploads"
    versions_dir: str = "versions"
    reports_dir: str = "reports"
    logs_dir: str = "logs"
    columns: List[ColumnRule] = ANIMAL_CONTRACT_COLUMNS
    version_format: str = "v{major}.{minor}.{patch}"

CONFIG = SystemConfig()
