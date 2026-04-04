"""
Модуль валидации Excel файлов с контрактами.
Проверяет структуру, типы данных, полноту и уникальность.
"""

import pandas as pd
from datetime import datetime
from typing import Tuple, List, Dict
from pathlib import Path
from config import CONFIG, DataType, ColumnRule

class ValidationResult:
    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict = {}

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

class ContractValidator:
    def __init__(self):
        self.config = CONFIG

    def validate_file(self, file_path: str) -> ValidationResult:
        """Полная валидация файла"""
        result = ValidationResult()
        
        # Проверка существования файла
        if not Path(file_path).exists():
            result.add_error(f"Файл не найден: {file_path}")
            return result

        try:
            # Чтение Excel
            df = pd.read_excel(file_path, engine='openpyxl')
            result.stats['total_rows'] = len(df)
            result.stats['total_columns'] = len(df.columns)
            
            # Валидация структуры
            self._validate_structure(df, result)
            
            if result.is_valid:
                # Валидация данных по колонкам
                self._validate_columns(df, result)
                
                # Валидация уникальности
                self._validate_uniqueness(df, result)
                
        except Exception as e:
            result.add_error(f"Ошибка чтения файла: {str(e)}")
            
        return result

    def _validate_structure(self, df: pd.DataFrame, result: ValidationResult):
        """Проверка наличия всех обязательных колонок"""
        expected_columns = {col.name for col in self.config.columns}
        actual_columns = set(df.columns)
        
        missing = expected_columns - actual_columns
        extra = actual_columns - expected_columns
        
        if missing:
            result.add_error(f"Отсутствуют обязательные колонки: {', '.join(missing)}")
        
        if extra:
            result.add_warning(f"Найдены лишние колонки: {', '.join(extra)}")

    def _validate_columns(self, df: pd.DataFrame, result: ValidationResult):
        """Проверка типов данных и значений"""
        for rule in self.config.columns:
            col = rule.name
            if col not in df.columns:
                continue
                
            series = df[col]
            
            # Проверка на пустые значения в обязательных полях
            if rule.required:
                null_count = series.isna().sum()
                if null_count > 0:
                    result.add_error(
                        f"Колонка '{col}': найдено {null_count} пустых значений (обязательное поле)"
                    )
            
            # Проверка типа данных
            if rule.dtype == DataType.STRING:
                self._validate_string_column(series, col, rule, result)
            elif rule.dtype == DataType.INTEGER:
                self._validate_numeric_column(series, col, rule, result, integer=True)
            elif rule.dtype == DataType.FLOAT:
                self._validate_numeric_column(series, col, rule, result, integer=False)
            elif rule.dtype == DataType.DATE:
                self._validate_date_column(series, col, result)
            elif rule.dtype == DataType.BOOLEAN:
                self._validate_boolean_column(series, col, result)
            
            # Проверка допустимых значений (справочник)
            if rule.allowed_values:
                self._validate_allowed_values(series, col, rule, result)

    def _validate_string_column(self, series: pd.Series, col: str, rule: ColumnRule, result: ValidationResult):
        """Валидация строковой колонки"""
        # Приводим к строке для проверки длины
        str_series = series.dropna().astype(str)
        
        if rule.min_length:
            too_short = str_series[str_series.str.len() < rule.min_length]
            if len(too_short) > 0:
                result.add_error(
                    f"Колонка '{col}': {len(too_short)} значений короче минимальной длины ({rule.min_length})"
                )
        
        if rule.max_length:
            too_long = str_series[str_series.str.len() > rule.max_length]
            if len(too_long) > 0:
                result.add_error(
                    f"Колонка '{col}': {len(too_long)} значений длиннее максимальной длины ({rule.max_length})"
                )

    def _validate_numeric_column(self, series: pd.Series, col: str, rule: ColumnRule, result: ValidationResult, integer: bool = False):
        """Валидация числовой колонки"""
        numeric_series = pd.to_numeric(series.dropna(), errors='coerce')
        invalid_count = numeric_series.isna().sum()
        
        if invalid_count > 0:
            result.add_error(
                f"Колонка '{col}': найдено {invalid_count} нечисловых значений"
            )

    def _validate_date_column(self, series: pd.Series, col: str, result: ValidationResult):
        """Валидация даты"""
        date_series = pd.to_datetime(series.dropna(), errors='coerce')
        invalid_count = date_series.isna().sum()
        
        # Учитываем только те, что были не пустыми изначально
        original_non_null = series.dropna()
        if len(original_non_null) > 0:
            converted_non_null = pd.to_datetime(original_non_null, errors='coerce')
            invalid_count = converted_non_null.isna().sum()
            
            if invalid_count > 0:
                result.add_error(
                    f"Колонка '{col}': найдено {invalid_count} некорректных дат (ожидается формат ГГГГ-ММ-ДД)"
                )

    def _validate_boolean_column(self, series: pd.Series, col: str, result: ValidationResult):
        """Валидация булевых значений"""
        valid_values = {True, False, 'True', 'False', 'true', 'false', 1, 0, '1', '0'}
        invalid_mask = ~series.dropna().isin(valid_values)
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            result.add_error(
                f"Колонка '{col}': найдено {invalid_count} некорректных булевых значений (ожидается True/False)"
            )

    def _validate_allowed_values(self, series: pd.Series, col: str, rule: ColumnRule, result: ValidationResult):
        """Проверка значений по справочнику"""
        allowed = set(rule.allowed_values)
        actual_values = set(series.dropna().unique())
        invalid_values = actual_values - allowed
        
        if invalid_values:
            result.add_error(
                f"Колонка '{col}': найдены недопустимые значения: {', '.join(map(str, invalid_values))}. "
                f"Допустимы: {', '.join(allowed)}"
            )

    def _validate_uniqueness(self, df: pd.DataFrame, result: ValidationResult):
        """Проверка уникальности колонок"""
        for rule in self.config.columns:
            if rule.unique and rule.name in df.columns:
                series = df[rule.name]
                duplicates = series[series.duplicated(keep=False)]
                if len(duplicates) > 0:
                    result.add_error(
                        f"Колонка '{rule.name}': найдено {len(duplicates)} дублирующихся значений (требуется уникальность)"
                    )

    def get_diff_report(self, old_file: str, new_file: str) -> Dict:
        """Сравнение двух версий файла"""
        try:
            df_old = pd.read_excel(old_file, engine='openpyxl')
            df_new = pd.read_excel(new_file, engine='openpyxl')
        except Exception as e:
            return {"error": f"Ошибка чтения файлов: {str(e)}"}
        
        report = {
            "added_rows": 0,
            "removed_rows": 0,
            "modified_rows": 0,
            "unchanged_rows": 0,
            "details": []
        }
        
        # Простое сравнение по количеству строк
        report["added_rows"] = max(0, len(df_new) - len(df_old))
        report["removed_rows"] = max(0, len(df_old) - len(df_new))
        
        # Более детальное сравнение можно добавить здесь
        # Например, сравнение по ключевому полю contract_id
        
        return report
